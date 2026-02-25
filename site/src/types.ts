export type Lang = 'en' | 'cn';

export type ReportIndexRecord = {
  report_id: string;
  path: string;
  languages: string[];
  group: string;
  updated_at: string;
};

export type WebIndex = {
  version: string;
  generated_at: string;
  reports: ReportIndexRecord[];
};

export type AssetRecord = {
  kind: 'pdf' | 'tex' | 'figure' | 'data' | 'other';
  label: string;
  web_path: string;
  source_path: string;
  size: number;
  sha256: string;
};

export type DatasetMeta = {
  series_id: string;
  title: string;
  x_label: string;
  y_label: string;
  series_path: string;
  default_series?: string[];
  series_semantics?: Array<{
    name: string;
    series_type: 'metric' | 'probability' | 'binary' | 'parameter';
    unit: string;
    min: number;
    max: number;
    positive_ratio: number;
  }>;
  provenance: {
    type: string;
    source: string;
  };
};

export type ReportMeta = {
  report_id: string;
  lang: string;
  title: string;
  summary: string;
  key_findings: string[];
  narrative: {
    model_overview: string;
    method_overview: string;
    result_overview: string;
  };
  section_cards: Array<{
    heading: string;
    summary: string;
    source_path: string;
  }>;
  math_blocks: Array<{
    latex: string;
    context: string;
    source_path: string;
    lang: Lang;
  }>;
  math_story: Array<{
    stage: string;
    description: string;
    latex: string;
    context: string;
  }>;
  reproducibility_commands: string[];
  source_documents: string[];
  datasets: DatasetMeta[];
  assets: AssetRecord[];
  updated_at: string;
};

export type SeriesPayload = {
  report_id: string;
  series_id: string;
  x_label: string;
  y_label: string;
  series: Array<{
    name: string;
    x: Array<number | string>;
    y: number[];
    series_type?: 'metric' | 'probability' | 'binary' | 'parameter';
    unit?: string;
  }>;
  series_semantics?: Array<{
    name: string;
    series_type: 'metric' | 'probability' | 'binary' | 'parameter';
    unit: string;
    min: number;
    max: number;
    positive_ratio: number;
  }>;
  default_series?: string[];
  provenance: {
    type: string;
    source: string;
  };
};

export type FigureRecord = {
  id: string;
  title: string;
  web_path: string;
  source_path: string;
};

export type AgentManifest = {
  version: string;
  generated_at: string;
  report_count: number;
  files: {
    reports_jsonl: string;
    events_jsonl: string;
    book_manifest: string;
    book_chapters_jsonl: string;
    claim_graph_jsonl: string;
    book_claim_coverage: string;
    translation_qc: string;
    theory_map: string;
    guide_json: string;
    report_network: string;
    content_map: string;
  };
};

export type BookClaimCoverage = {
  version: string;
  generated_at: string;
  policy_en: string;
  policy_cn: string;
  global_claim_count: number;
  chapter_claim_count: number;
  chapter_total_claim_count?: number;
  chapter_native_claim_count?: number;
  excluded_claim_count: number;
  chapter_claim_ids: string[];
  chapter_native_claim_ids?: string[];
  excluded_claim_ids: string[];
};

export type ReportNetwork = {
  version: string;
  generated_at: string;
  notion_labels: Record<
    string,
    {
      label_en: string;
      label_cn: string;
    }
  >;
  group_paths: Array<{
    group: string;
    report_ids: string[];
    step_count: number;
  }>;
  global_storyline: {
    label_en: string;
    label_cn: string;
    report_ids: string[];
  };
  reports: Array<{
    report_id: string;
    group: string;
    title_en: string;
    title_cn: string;
    summary_en: string;
    summary_cn: string;
    notion_ids: string[];
    previous_in_group: string;
    next_in_group: string;
    same_group_links: Array<{
      report_id: string;
      score: number;
      same_group: boolean;
      adjacent_in_track: boolean;
      shared_notion_ids: string[];
      shared_token_count: number;
    }>;
    cross_group_links: Array<{
      report_id: string;
      score: number;
      same_group: boolean;
      adjacent_in_track: boolean;
      shared_notion_ids: string[];
      shared_token_count: number;
    }>;
  }>;
};

export type TheoryMap = {
  version: string;
  generated_at: string;
  cards: Array<{
    id: string;
    label_en: string;
    label_cn: string;
    description_en: string;
    description_cn: string;
    report_ids: string[];
    report_count: number;
  }>;
  consistency_checks: Array<{
    check: string;
    pass: boolean;
    details: unknown;
  }>;
};

export type ContentMap = {
  version: string;
  generated_at: string;
  report_count: number;
  arcs: Array<{
    arc_id: string;
    label_en: string;
    label_cn: string;
    summary_en: string;
    summary_cn: string;
    report_ids: string[];
    claim_ids: string[];
    checkpoint_count: number;
    checkpoints: Array<{
      report_id: string;
      title_en: string;
      title_cn: string;
      contribution_en: string;
      contribution_cn: string;
    }>;
  }>;
  claims: Array<{
    claim_id: string;
    report_id: string;
    stage: 'model' | 'method' | 'result' | 'finding';
    text_en: string;
    text_cn: string;
    evidence: Array<{
      evidence_type: 'source_document' | 'section_summary' | 'math_block' | 'dataset';
      path: string;
      snippet_en: string;
      snippet_cn: string;
    }>;
    linked_claim_ids: string[];
    linked_report_ids: string[];
  }>;
  report_guides: Array<{
    report_id: string;
    objective_en: string;
    objective_cn: string;
    upstream_report_ids: string[];
    downstream_report_ids: string[];
    related_report_ids: string[];
    verification_steps_en: string[];
    verification_steps_cn: string[];
  }>;
  consistency_checks: Array<{
    check: string;
    pass: boolean;
    details: unknown;
  }>;
};

export type BookManifest = {
  version: string;
  generated_at: string;
  chapter_count: number;
  chapters: Array<{
    chapter_id: string;
    order: number;
    slug: string;
    title_en: string;
    title_cn: string;
    summary_en: string;
    summary_cn: string;
    report_ids: string[];
    concept_ids: string[];
    interactive_count: number;
    claim_count: number;
    estimated_read_minutes: number;
    previous_chapter_id: string | null;
    next_chapter_id: string | null;
  }>;
  toc: {
    en: Array<{ chapter_id: string; order: number; title: string; path: string }>;
    cn: Array<{ chapter_id: string; order: number; title: string; path: string }>;
  };
  report_chapter_map: Record<
    string,
    {
      primary_chapter_id: string;
      chapter_ids: string[];
    }
  >;
  quality_checks: Array<{
    check: string;
    pass: boolean;
    details: unknown;
  }>;
};

export type BookChapter = {
  chapter_id: string;
  order: number;
  slug: string;
  title_en: string;
  title_cn: string;
  kicker_en: string;
  kicker_cn: string;
  intro_en: string[];
  intro_cn: string[];
  concept_cards: Array<{
    id: string;
    label_en: string;
    label_cn: string;
    description_en: string;
    description_cn: string;
    report_ids: string[];
  }>;
  theory_chain: Array<{
    report_id: string;
    stage: string;
    label_en: string;
    label_cn: string;
    description_en: string;
    description_cn: string;
    latex: string;
    context: string;
  }>;
  interactive_panels: Array<{
    panel_id: string;
    report_id: string;
    title_en: string;
    title_cn: string;
    dataset_series_id: string;
    dataset_path: string;
    x_label: string;
    y_label: string;
    parameter_hint_en: string;
    parameter_hint_cn: string;
  }>;
  linked_reports: Array<{
    report_id: string;
    group: string;
    title_en: string;
    title_cn: string;
    summary_en: string;
    summary_cn: string;
    book_role_en: string;
    book_role_cn: string;
  }>;
  claim_ledger: Array<{
    claim_id: string;
    report_id: string;
    stage: 'model' | 'method' | 'result' | 'finding';
    text_en: string;
    text_cn: string;
    evidence: Array<{
      evidence_type: string;
      path: string;
      snippet_en: string;
      snippet_cn: string;
    }>;
    linked_report_ids: string[];
  }>;
  summary_en: string;
  summary_cn: string;
  previous_chapter_id: string | null;
  next_chapter_id: string | null;
  source_paths: string[];
  updated_at: string;
};

export type BookBackbone = {
  version: string;
  generated_at: string;
  chapter_count: number;
  acts: Array<{
    act_id: string;
    title_en: string;
    title_cn: string;
    objective_en: string;
    objective_cn: string;
    chapter_ids: string[];
  }>;
  chapter_spine: Array<{
    chapter_id: string;
    order: number;
    title_en: string;
    title_cn: string;
    core_question_en: string;
    core_question_cn: string;
    input_dependencies: string[];
    output_to: string[];
    key_claim_ids: string[];
    key_formulae: string[];
    key_notions: string[];
    evidence_report_ids: string[];
    transition_to_next_en: string;
    transition_to_next_cn: string;
    interactive_count: number;
    claim_count: number;
    formula_count: number;
  }>;
  quality_checks: Array<{
    check: string;
    pass: boolean;
    details: unknown;
  }>;
};

export type GlossaryPayload = {
  version: string;
  generated_at: string;
  term_count: number;
  terms: Array<{
    term_id: string;
    category: string;
    term_en: string;
    term_cn: string;
    definition_en: string;
    definition_cn: string;
    aliases_en: string[];
    aliases_cn: string[];
    locked: boolean;
    formula?: string;
    related_report_ids: string[];
    related_chapter_ids: string[];
    provenance: Array<{
      type: string;
      source: string;
    }>;
  }>;
};

export type TranslationQC = {
  version: string;
  generated_at: string;
  passed: boolean;
  thresholds: {
    high_max: number;
    warning_max: number;
  };
  stats: {
    scanned_text_blocks: number;
    high: number;
    warning: number;
  };
  issues: Array<{
    severity: 'high' | 'warning';
    scope: 'report' | 'book' | 'global';
    location: string;
    lang: Lang;
    field: string;
    excerpt: string;
    message: string;
  }>;
};
