/**
 * Validate docs/review-form.gs against the real Apps Script API surface.
 *
 * The first version of this check stubbed FormApp with a Proxy that returned a
 * function for any property, so every method call succeeded, including
 * setShowLinkToRespondAnother -- which does not exist. That typo reached Google
 * before anything caught it.
 *
 * This stub is an allowlist instead: only methods that FormApp genuinely
 * publishes are callable, and anything else throws with the offending name.
 *
 *   node backend/tools/validate_review_form.js
 */
'use strict';

const fs = require('fs');
const path = require('path');

const FORM_FILE = path.join(__dirname, '..', '..', 'docs', 'review-form.gs');

// https://developers.google.com/apps-script/reference/forms
const FORM_METHODS = [
  'addCheckboxGridItem', 'addCheckboxItem', 'addDateItem', 'addDateTimeItem',
  'addDurationItem', 'addGridItem', 'addImageItem', 'addListItem',
  'addMultipleChoiceItem', 'addPageBreakItem', 'addParagraphTextItem',
  'addScaleItem', 'addSectionHeaderItem', 'addTextItem', 'addTimeItem',
  'addVideoItem', 'deleteItem', 'getDescription', 'getDestinationId',
  'getDestinationType', 'getEditUrl', 'getId', 'getItems', 'getPublishedUrl',
  'getTitle', 'removeDestination', 'setAcceptingResponses',
  'setAllowResponseEdits', 'setCollectEmail', 'setConfirmationMessage',
  'setCustomClosedFormMessage', 'setDescription', 'setDestination', 'setIsQuiz',
  'setLimitOneResponsePerUser', 'setProgressBar', 'setPublishingSummary',
  'setRequireLogin', 'setShowLinkToRespondAgain', 'setShuffleQuestions',
  'setTitle',
];

const ITEM_METHODS = [
  'createChoice', 'duplicate', 'getChoices', 'getHelpText', 'getId',
  'getIndex', 'getPoints', 'getTitle', 'getType', 'setChoiceValues',
  'setChoices', 'setHelpText', 'setPoints', 'setRequired', 'setTitle',
  'showOtherOption',
];

const SHEET_METHODS = ['getId', 'getUrl', 'getName', 'getSheets'];

let itemCount = 0;
const problems = [];

// Getters have to return a value rather than the proxy, or a logged URL
// prints as [object Object] and the check reads as passing when it is blind.
const GETTER_VALUES = {
  getId: '<id>',
  getUrl: '<url>',
  getName: '<name>',
  getTitle: '<title>',
  getHelpText: '<help>',
};

function strict(label, methods, onCall) {
  const target = {};
  for (const name of methods) {
    target[name] = function (...args) {
      if (onCall) onCall(name, args);
      if (name in GETTER_VALUES) return GETTER_VALUES[name];
      return proxy;
    };
  }
  const proxy = new Proxy(target, {
    get(obj, prop) {
      if (typeof prop === 'symbol' || prop === 'inspect') return undefined;
      if (!(prop in obj)) {
        problems.push(`${label}.${String(prop)} is not a real Apps Script method`);
        throw new TypeError(`${label}.${String(prop)} is not a function`);
      }
      return obj[prop];
    },
  });
  return proxy;
}

const item = () => strict('Item', ITEM_METHODS);

const formTarget = {};
for (const name of FORM_METHODS) {
  formTarget[name] = function (...args) {
    if (name.startsWith('add')) {
      itemCount++;
      return item();
    }
    if (name === 'getEditUrl') return '<edit url>';
    if (name === 'getPublishedUrl') return '<share url>';
    if (name === 'getId') return '<form id>';
    return formProxy;
  };
}
const formProxy = new Proxy(formTarget, {
  get(obj, prop) {
    if (typeof prop === 'symbol' || prop === 'inspect') return undefined;
    if (!(prop in obj)) {
      problems.push(`Form.${String(prop)} is not a real Apps Script method`);
      throw new TypeError(`Form.${String(prop)} is not a function`);
    }
    return obj[prop];
  },
});

global.FormApp = {
  create: () => formProxy,
  DestinationType: { SPREADSHEET: 'SPREADSHEET' },
  ItemType: {},
};
global.SpreadsheetApp = { create: () => strict('Spreadsheet', SHEET_METHODS) };

const logs = [];
global.Logger = { log: (m) => logs.push(String(m)) };

const source = fs.readFileSync(FORM_FILE, 'utf8');

try {
  // eslint-disable-next-line no-eval
  eval(source + '\nbuildReviewForm();');
} catch (err) {
  console.error('FAILED: ' + err.message);
  problems.forEach((p) => console.error('  - ' + p));
  process.exit(1);
}

if (problems.length) {
  console.error('FAILED');
  problems.forEach((p) => console.error('  - ' + p));
  process.exit(1);
}

console.log('review-form.gs validated against the real FormApp API');
console.log('  form items created : ' + itemCount);
logs.forEach((l) => console.log('  ' + l));

// Google Forms rejects a form with more than 300 items.
if (itemCount >= 300) {
  console.error(`FAILED: ${itemCount} items exceeds the Google Forms limit of 300`);
  process.exit(1);
}
