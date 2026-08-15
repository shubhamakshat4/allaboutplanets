import { forwardRef, useId, useState, type ReactNode } from 'react'
import { cn, isUnknown } from '@/lib/utils'

/* --- Card ---------------------------------------------------------------- */
export function Card({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'panel print-avoid-break',
        className,
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export function CardHeader({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <div className={cn('border-b border-black/5 px-5 py-3.5', className)}>{children}</div>
  )
}

export function CardTitle({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <h3 className={cn('font-display text-lg font-bold text-ink-800', className)}>
      {children}
    </h3>
  )
}

export function CardBody({ className, children }: { className?: string; children: ReactNode }) {
  return <div className={cn('px-5 py-4', className)}>{children}</div>
}

/* --- Button -------------------------------------------------------------- */
type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'ghost' | 'outline' | 'soft' | 'glass'
  size?: 'sm' | 'md' | 'lg'
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'secondary', size = 'md', ...props }, ref) => (
    <button
      ref={ref}
      className={cn(
        'inline-flex items-center justify-center gap-1.5 rounded-full font-bold',
        'transition-all active:scale-[.97]',
        'disabled:cursor-not-allowed disabled:opacity-50 disabled:active:scale-100',
        {
          primary:
            'bg-gradient-to-r from-sun-500 to-orange-500 text-white shadow-card hover:shadow-lift',
          secondary: 'bg-white text-ink-700 border border-black/10 shadow-sm hover:bg-cream-100',
          outline: 'bg-transparent text-ink-600 border border-black/15 hover:bg-white',
          ghost: 'bg-transparent text-ink-500 hover:bg-black/5',
          soft: 'bg-white/85 text-ink-700 border border-black/10 shadow-sm hover:bg-white',
          glass: 'bg-white/25 text-white border border-white/40 backdrop-blur hover:bg-white/35',
        }[variant],
        { sm: 'h-8 px-3.5 text-[13px]', md: 'h-10 px-5 text-sm', lg: 'h-12 px-7 text-[15px]' }[size],
        className,
      )}
      {...props}
    />
  ),
)
Button.displayName = 'Button'

/* --- Input / Select / Label ---------------------------------------------- */
export const Input = forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        'h-11 w-full rounded-xl border border-black/10 bg-white px-4 text-[15px] shadow-sm',
        'placeholder:text-ink-400 focus:border-sun-400',
        'disabled:bg-black/5 disabled:text-ink-400',
        className,
      )}
      {...props}
    />
  ),
)
Input.displayName = 'Input'

export const Select = forwardRef<
  HTMLSelectElement,
  React.SelectHTMLAttributes<HTMLSelectElement>
>(({ className, ...props }, ref) => (
  <select
    ref={ref}
    className={cn(
      'h-11 w-full rounded-xl border border-black/10 bg-white px-3 text-[15px] shadow-sm',
      'focus:border-sun-400',
      className,
    )}
    {...props}
  />
))
Select.displayName = 'Select'

export function Label({
  className, children, htmlFor,
}: { className?: string; children: ReactNode; htmlFor?: string }) {
  return (
    <label htmlFor={htmlFor} className={cn('label mb-1 block', className)}>
      {children}
    </label>
  )
}

/* --- Field: the label/value pair used throughout the analysis ------------- */
export function Field({
  label, value, mono, hint, className,
}: {
  label: string
  value: ReactNode
  mono?: boolean
  hint?: string
  className?: string
}) {
  const unknown = typeof value === 'string' && isUnknown(value)
  return (
    <div className={cn('min-w-0', className)}>
      <dt className="label">{label}</dt>
      <dd
        className={cn(
          'mt-1 break-words font-semibold',
          mono ? 'value-mono' : 'value',
          unknown && 'italic text-ink-400',
        )}
      >
        {value}
      </dd>
      {hint && <p className="mt-0.5 text-[11px] leading-snug text-ink-400">{hint}</p>}
    </div>
  )
}

export function FieldGrid({
  cols = 3, className, children,
}: { cols?: 2 | 3 | 4; className?: string; children: ReactNode }) {
  return (
    <dl
      className={cn(
        'grid gap-x-6 gap-y-4',
        { 2: 'sm:grid-cols-2', 3: 'sm:grid-cols-2 lg:grid-cols-3', 4: 'sm:grid-cols-2 lg:grid-cols-4' }[cols],
        className,
      )}
    >
      {children}
    </dl>
  )
}

/* --- Badge --------------------------------------------------------------- */
export function Badge({
  children, className, title,
}: { children: ReactNode; className?: string; title?: string }) {
  return (
    <span
      title={title}
      className={cn(
        'inline-flex items-center rounded border px-1.5 py-0.5',
        'text-[11px] font-medium leading-none whitespace-nowrap',
        'border-black/10 bg-black/[.04] text-ink-600',
        className,
      )}
    >
      {children}
    </span>
  )
}

/** Yes/No/Not-defined presented as a neutral chip. */
export function BoolBadge({ value }: { value: boolean | string | null | undefined }) {
  if (value === true) {
    return <Badge className="border-ink-800 bg-ink-800 text-white">Yes</Badge>
  }
  if (value === false) {
    return <Badge className="border-ink-200 bg-white text-ink-500">No</Badge>
  }
  return (
    <span className="text-[11px] italic text-ink-400">
      {value === null || value === undefined ? 'Not available' : String(value)}
    </span>
  )
}

/* --- Status pill for conditions and yogas -------------------------------- */
export function StatusPill({ status }: { status: string }) {
  const tone =
    status === 'Satisfied' || status === 'Present'
      ? 'border-good-600 bg-good-600 text-white'
      : status === 'Not satisfied' || status === 'Not Present'
        ? 'border-black/10 bg-white text-ink-500'
        : 'border-calm-200 bg-calm-50 text-calm-700 italic'
  return <Badge className={tone}>{status}</Badge>
}

/* --- Tooltip (CSS only, no dependency) ----------------------------------- */
export function Tooltip({ label, children }: { label: string; children: ReactNode }) {
  return (
    <span className="group relative inline-flex items-center">
      {children}
      <span
        role="tooltip"
        className={cn(
          'pointer-events-none absolute bottom-full left-1/2 z-30 mb-1.5 hidden',
          '-translate-x-1/2 whitespace-pre rounded-md bg-ink-900 px-2 py-1.5',
          'text-[11px] font-normal leading-snug text-ink-50 shadow-lg',
          'group-hover:block group-focus-within:block no-print',
        )}
      >
        {label}
      </span>
    </span>
  )
}

/* --- Section: collapsible, with a stable open/close API ------------------ */
export function Section({
  id, title, subtitle, sectionLetter, children, open, onToggle, actions, count,
}: {
  id: string
  title: string
  subtitle?: string
  sectionLetter?: string
  children: ReactNode
  open: boolean
  onToggle: (id: string) => void
  actions?: ReactNode
  count?: number
}) {
  return (
    <Card id={id} className="scroll-mt-24">
      <div className="flex items-center gap-3 border-b border-ink-200 px-5 py-3">
        <button
          type="button"
          onClick={() => onToggle(id)}
          aria-expanded={open}
          aria-controls={`${id}-panel`}
          className="flex min-w-0 flex-1 items-center gap-3 text-left"
        >
          <span
            className={cn(
              'grid h-6 w-6 shrink-0 place-items-center rounded-lg bg-black/5',
              'text-[11px] font-bold text-ink-500 transition-transform',
              open && 'rotate-90',
            )}
            aria-hidden
          >
            ›
          </span>
          {sectionLetter && (
            <span className="shrink-0 font-mono text-[11px] font-medium text-accent-600">
              {sectionLetter}
            </span>
          )}
          <span className="min-w-0">
            <span className="block font-serif text-base font-semibold text-ink-900">
              {title}
              {typeof count === 'number' && (
                <span className="ml-2 font-sans text-xs font-normal text-ink-400">
                  {count}
                </span>
              )}
            </span>
            {subtitle && (
              <span className="mt-0.5 block text-[12.5px] text-ink-400">{subtitle}</span>
            )}
          </span>
        </button>
        {actions && <div className="shrink-0 no-print">{actions}</div>}
      </div>
      <div
        id={`${id}-panel`}
        className={cn('print-open', open ? 'block' : 'hidden')}
      >
        <div className="px-5 py-4">{children}</div>
      </div>
    </Card>
  )
}

/* --- Evidence disclosure ------------------------------------------------- */
export function Evidence({
  children, label = 'How calculated?', rule, source,
}: {
  children: ReactNode
  label?: string
  rule?: string | null
  source?: string
}) {
  const id = useId()
  const [open, setOpen] = useState(false)
  return (
    <div className="mt-2">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        aria-controls={id}
        className={cn(
          'inline-flex items-center gap-1 rounded text-[11px] font-medium',
          'text-sun-600 hover:text-sun-500 hover:underline no-print',
        )}
      >
        <span aria-hidden className={cn('transition-transform', open && 'rotate-90')}>›</span>
        {label}
      </button>
      <div
        id={id}
        className={cn(
          'print-open mt-1.5 rounded-xl border border-black/10 bg-cream-100/70 px-3.5 py-3',
          open ? 'block' : 'hidden',
        )}
      >
        <div className="space-y-1.5 text-[12px] leading-relaxed text-ink-700">{children}</div>
        {(rule || source) && (
          <div className="mt-2 flex flex-wrap gap-1.5 border-t border-ink-200 pt-2">
            {source && <Badge title="Where this value comes from">Source: {source}</Badge>}
            {rule && <Badge title="Rule identifier in the rule registry">Rule: {rule}</Badge>}
          </div>
        )}
      </div>
    </div>
  )
}

/* --- Table --------------------------------------------------------------- */
export function TableWrap({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={cn('-mx-4 overflow-x-auto px-4 sm:mx-0 sm:px-0', className)}>
      {children}
    </div>
  )
}

export function Table({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <table className={cn('w-full border-collapse text-sm', className)}>{children}</table>
  )
}

export function Th({
  children, className, align = 'left', title,
}: {
  children: ReactNode
  className?: string
  align?: 'left' | 'right' | 'center'
  title?: string
}) {
  return (
    <th
      title={title}
      className={cn(
        'whitespace-nowrap border-b-2 border-black/10 px-2.5 py-2',
        'label',
        { left: 'text-left', right: 'text-right', center: 'text-center' }[align],
        className,
      )}
    >
      {children}
    </th>
  )
}

export function Td({
  children, className, align = 'left', mono,
}: {
  children: ReactNode
  className?: string
  align?: 'left' | 'right' | 'center'
  mono?: boolean
}) {
  return (
    <td
      className={cn(
        'border-b border-black/5 px-2.5 py-2 align-top',
        mono && 'font-mono tabular text-[13px]',
        { left: 'text-left', right: 'text-right', center: 'text-center' }[align],
        className,
      )}
    >
      {children}
    </td>
  )
}

/* --- Empty / message states ---------------------------------------------- */
export function Empty({ children }: { children: ReactNode }) {
  return (
    <p className="rounded-md border border-dashed border-ink-200 bg-ink-50 px-3 py-4 text-center text-[13px] text-ink-500">
      {children}
    </p>
  )
}

export function Note({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <p
      className={cn(
        'rounded-xl border-l-4 border-sun-400 bg-sun-400/10 px-4 py-2.5',
        'text-[12px] leading-relaxed text-ink-700',
        className,
      )}
    >
      {children}
    </p>
  )
}

export function ErrorBox({ children }: { children: ReactNode }) {
  return (
    <div
      role="alert"
      className="rounded-xl border border-hard-300 bg-hard-50 px-4 py-3 text-sm font-semibold text-hard-800"
    >
      {children}
    </div>
  )
}

export function Spinner({ label }: { label?: string }) {
  return (
    <div className="flex items-center justify-center gap-2.5 py-10 text-sm text-ink-500">
      <span
        aria-hidden
        className="h-5 w-5 animate-spin rounded-full border-[3px] border-sun-400/30 border-t-sun-500"
      />
      {label ?? 'Calculating…'}
    </div>
  )
}
