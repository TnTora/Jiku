/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type KnownStatus = 1 | 0;

export interface LastSessionResponse {
  lines: LineBase[];
  status_map: {
    [k: string]: KnownStatus;
  };
}
export interface LineBase {
  id: number;
  text: string;
  tokens: Morpheme[];
}
export interface Morpheme {
  lemma: string;
  inflection: string;
  pos?: string;
  tag?: string;
}
export interface LineCreate {
  text: string;
  preset: string | null;
}
export interface LineResponse {
  id: number;
  text: string;
  date_added: string;
  tokens: Morpheme[];
  line_status_map: {
    [k: string]: KnownStatus;
  };
}
export interface PresetCreate {
  name: string;
  ws_url: string;
}
export interface PresetInfo {
  name: string;
  ws_url: string;
}
export interface PresetRename {
  old_name: string;
  new_name: string;
}
export interface PresetUpdate {
  name: string;
  ws_url: string;
}
