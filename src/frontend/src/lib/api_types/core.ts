/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface AnkiInfo {
  decks?: string[];
  note_types?: string[];
  note_types_fields?: {
    [k: string]: string[];
  };
}
export interface AnkiInfoRespone {
  decks: string[];
  note_types: string[];
  note_types_fields: {
    [k: string]: string[];
  };
}
export interface AnkiSettings {
  port?: number;
  to_analyze?: SearchParameters[];
  to_update?: [unknown, unknown][];
}
export interface SearchParameters {
  deck: string;
  note_type: string;
  text_field: string;
  skip_brackets?: boolean;
}
export interface AnkiSettingsRespone {
  port: number;
  to_analyze: SearchParameters[];
  to_update: [unknown, unknown][];
}
export interface KnownMorphemes {
  lemmas: number;
  inflections: number;
}
export interface Morpheme {
  lemma: string;
  inflection: string;
  pos?: string;
  tag?: string;
}
export interface SearchParametersRespone {
  deck: string;
  note_type: string;
  text_field: string;
  skip_brackets: boolean;
}
