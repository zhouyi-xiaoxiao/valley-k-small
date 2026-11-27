// Typesetting of reader-facing text. No file-system access, so the client
// chart panel can use it too; `atlas.ts` re-exports everything here.
import { Fragment, createElement, type ReactNode } from 'react';

/** Straight apostrophes between two letters become ’ (shortcut's → shortcut’s). */
export function typesetApostrophes(text: string): string {
  return text.replace(/(?<=\p{L})'(?=\p{L})/gu, '’');
}

const MONTHS = 'January|February|March|April|May|June|July|August|September|October|November|December';
const SPACE = '[ \\u00a0\\u202f]';
// One symbol: a letter with sub- or superscripts and an argument (f(t), q₁, t_v, rᵀ), a tuple, or a number.
const SYMBOL =
  '(?:[A-Za-zα-ωΑ-Ω](?:[₀-₉ₐ-ₜᵢ-ᵥ′ᵀ⁰-⁹¹²³⁻⁺]|_\\{?[A-Za-z0-9]+\\}?|\\^\\{?[A-Za-z0-9−-]+\\}?)*(?:\\([^()\\s]{1,12}\\))?' +
  '|\\([^()\\s]{1,12}\\)' +
  '|[−-]?\\d[\\d.,]*[⁰-⁹¹²³⁻]*)';
// The right-hand side stops at Chinese characters and full-width punctuation, so that a
// bracket of Chinese text after the value (K = 2（…）) stays outside the no-wrap span.
const RHS = '[^\\s,;:)\\u3000-\\u303f\\u3400-\\u9fff\\uff00-\\uffef]{1,24}';
// A run without spaces, Chinese characters or full-width punctuation.
const WORD = '[^\\s\\u3000-\\u303f\\u3400-\\u9fff\\uff00-\\uffef]+';
const OPERATOR = '(?:=|≈|≠|≤|≥|<|>|∈|→|×|±|−|\\+)';
const KEEP_TOGETHER = new RegExp(
  [
    // Equations and relations: K = 4, N = 100, β = 0.01, 0.0005 ≤ β ≤ 0.05, 60 × 60.
    `(?<![\\p{L}\\p{N}_])${SYMBOL}${SPACE}?${OPERATOR}${SPACE}?${RHS}(?:${SPACE}?${OPERATOR}${SPACE}?${RHS}){0,2}`,
    // Dates: 15 April 2026.
    `(?<!\\p{N})\\d{1,2}${SPACE}(?:${MONTHS})(?:${SPACE}\\d{4})?(?!\\p{L})`,
    // Labels with a number: Fig. 1, Eq. 3, Chapter 2, Case A.
    `\\b(?:Figs?|Eqs?|Secs?|Refs?|No)\\.${SPACE}\\d+[a-z]?(?!\\p{N})`,
    `\\b(?:Figure|Table|Chapter|Section|Case|Stage|Study|Act|Part)${SPACE}(?:\\d+[a-z]?|[A-Z]\\d?|[IVX]+)(?![\\p{L}\\p{N}])`,
    // Numbers with a space as thousands separator, and a number with its unit.
    `(?<![\\p{N}.,])\\d{1,3}(?:${SPACE}\\d{3})+(?![\\p{N}])`,
    `(?<![\\p{L}\\p{N}_])\\d[\\d.,]*${SPACE}(?:%|‰|ms|s|min|h|kB|KB|MB|GB|px)(?![\\p{L}\\p{N}])`,
    // Anything else the source joined with a no-break space. Chinese characters
    // and full-width punctuation are left out: a run of them has no spaces and
    // would otherwise become one long unbreakable span.
    `${WORD}(?:[\\u00a0\\u202f]${WORD})+`,
  ].join('|'),
  'gu',
);

/**
 * Short equations and labels ("K = 4", "N = 100", "Fig. 1", "15 April 2026",
 * a number and its unit) must not break across lines. They are wrapped in a
 * no-wrap span with ordinary spaces: a no-break space renders wider than a
 * normal space in the body font, which gave the doubled gaps on desktop.
 */
export function keepTogether(text: string): ReactNode {
  if (!text) {
    return text;
  }
  const parts: ReactNode[] = [];
  let last = 0;
  for (const match of text.matchAll(KEEP_TOGETHER)) {
    const start = match.index ?? 0;
    const value = match[0];
    if (!/[   ]/.test(value)) {
      continue;
    }
    if (start > last) {
      parts.push(text.slice(last, start));
    }
    parts.push(
      createElement('span', { key: `kt-${start}`, className: 'keep-together' }, value.replace(/[   ]+/g, ' ')),
    );
    last = start + value.length;
  }
  if (parts.length === 0) {
    return text;
  }
  if (last < text.length) {
    parts.push(text.slice(last));
  }
  return createElement(Fragment, null, ...parts);
}

/** Text as shown to readers: curly apostrophes, equations kept on one line. */
export function readerText(text: string): ReactNode {
  return keepTogether(typesetApostrophes(text));
}

// ---------------------------------------------------------------------------
// Inline mathematics written as $…$ in extracted report text.

/** One inline formula between dollar signs. */
export const INLINE_MATH = /\$[^$\n]+\$/g;

/** The text with every $…$ span replaced by a space, for checks that look at the prose only. */
export function withoutInlineMath(text: string): string {
  return text.replace(INLINE_MATH, ' ');
}

const PLAIN_COMMANDS: Record<string, string> = {
  alpha: 'α', beta: 'β', gamma: 'γ', delta: 'δ', epsilon: 'ε', varepsilon: 'ε', eta: 'η', theta: 'θ',
  kappa: 'κ', lambda: 'λ', mu: 'μ', nu: 'ν', pi: 'π', rho: 'ρ', sigma: 'σ', tau: 'τ', phi: 'φ',
  varphi: 'φ', chi: 'χ', psi: 'ψ', omega: 'ω', Gamma: 'Γ', Delta: 'Δ', Theta: 'Θ', Lambda: 'Λ',
  Sigma: 'Σ', Phi: 'Φ', Psi: 'Ψ', Omega: 'Ω',
  le: '≤', leq: '≤', ge: '≥', geq: '≥', ne: '≠', neq: '≠', approx: '≈', sim: '∼', to: '→',
  rightarrow: '→', leftarrow: '←', in: '∈', times: '×', cdot: '·', pm: '±', infty: '∞',
  lfloor: '⌊', rfloor: '⌋', lceil: '⌈', rceil: '⌉', ldots: '…', cdots: '…', mid: '|',
  quad: ' ', qquad: ' ',
};

const SUBSCRIPTS: Record<string, string> = {
  '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄', '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
  '+': '₊', '-': '₋', '=': '₌', '(': '₍', ')': '₎', a: 'ₐ', e: 'ₑ', h: 'ₕ', i: 'ᵢ', j: 'ⱼ', k: 'ₖ',
  l: 'ₗ', m: 'ₘ', n: 'ₙ', o: 'ₒ', p: 'ₚ', r: 'ᵣ', s: 'ₛ', t: 'ₜ', u: 'ᵤ', v: 'ᵥ', x: 'ₓ',
};
const SUPERSCRIPTS: Record<string, string> = {
  '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
  '+': '⁺', '-': '⁻', '=': '⁼', '(': '⁽', ')': '⁾', i: 'ⁱ', n: 'ⁿ', T: 'ᵀ',
};

// q_i → qᵢ, t_{max} → tₘₐₓ; a script with no Unicode form stays as _stay, or _(…) when it holds operators.
function plainScript(body: string, marks: Record<string, string>, sign: string): string {
  const chars = [...body];
  if (chars.every((c) => marks[c])) {
    return chars.map((c) => marks[c]).join('');
  }
  return /^[A-Za-z0-9]+$/.test(body) ? `${sign}${body}` : `${sign}(${body})`;
}

/**
 * A $…$ span as plain text, for places that cannot hold markup (page titles,
 * meta descriptions, aria labels): the dollar signs go, font commands keep
 * their argument (\text{stay} → stay), common commands become their symbol,
 * simple sub- and superscripts become Unicode, and the remaining backslashes
 * and braces are dropped.
 */
export function plainMath(latex: string): string {
  return latex
    .replace(/\\(?:text|mathrm|mathbf|mathit|mathsf|operatorname|boldsymbol)\s*\{([^{}]*)\}/g, '$1')
    .replace(/\\(?:left|right|big|Big)(?![A-Za-z])/g, '')
    .replace(/\\\{/g, '\u0001').replace(/\\\}/g, '\u0002')
    .replace(/\\[,;:! ]/g, ' ')
    .replace(/\\([A-Za-z]+)/g, (_match, name: string) => PLAIN_COMMANDS[name] ?? name)
    .replace(/_\{([^{}]*)\}|_(.)/g, (_match, group: string | undefined, single: string | undefined) =>
      plainScript(group ?? single ?? '', SUBSCRIPTS, '_'),
    )
    .replace(/\^\{([^{}]*)\}|\^(.)/g, (_match, group: string | undefined, single: string | undefined) =>
      plainScript(group ?? single ?? '', SUPERSCRIPTS, '^'),
    )
    .replace(/[{}]/g, '')
    .replace(/\u0001/g, '{').replace(/\u0002/g, '}')
    .replace(/\s+/g, ' ')
    .trim();
}

/** Text with each $…$ span replaced by its plain form. */
export function plainText(text: string): string {
  return text.replace(INLINE_MATH, (span) => plainMath(span.slice(1, -1)));
}
