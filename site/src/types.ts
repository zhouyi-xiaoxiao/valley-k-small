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
    theory_map: string;
    guide_json: string;
    report_network?: string;
    content_map?: string;
  };
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
