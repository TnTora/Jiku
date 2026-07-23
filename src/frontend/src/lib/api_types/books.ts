/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface Book {
  id: number;
  title: string;
  raw_metadata: {
    [k: string]: unknown;
  } | null;
  sections: {
    [k: string]: Section;
  };
  stylesheets: string[];
  spine: string[];
  toc: TocItem[];
  bookmarks: BookmarkResponse[];
  thumb: string | null;
  original_file: string;
  static_url: string;
  total_char: number;
  total_tokens: number;
  date_added: string;
  last_opened: string;
  last_pos: BookPosition | null;
}
export interface Section {
  key: string;
  number: number;
  stylesheets: string[];
  filename: string;
  start_ch: number;
  start_tok: number;
}
export interface TocItem {
  title: string;
  section: string;
  anchor_id?: string | null;
}
export interface BookmarkResponse {
  section: string;
  ch_pos?: number | null;
  tok_pos?: number | null;
  book_id: number;
  name: string;
  preview?: string | null;
  id: number;
}
export interface BookPosition {
  section: string;
  ch_pos?: number | null;
  tok_pos?: number | null;
}
export interface BookInfoResponse {
  id: number;
  title: string;
  creators?: string[];
  thumb?: string | null;
  static_url: string;
  progress_percent: number;
}
export interface BookKnownStats {
  total: number;
  unique: number;
  total_known: number;
  unique_known: number;
}
export interface BookLastOpenUpdate {
  id: number;
}
export interface BookLastPosUpdate {
  section: string;
  ch_pos?: number | null;
  tok_pos?: number | null;
  id: number;
}
export interface BookMetadata {
  title: string;
  authors: string[];
  raw: {
    [k: string]: unknown;
  };
}
export interface BookProcessCancel {
  id: string;
}
export interface BookProgressStatusUpdate {
  id: number;
  new_status: string;
}
export interface BookRespone {
  book: Book;
  status_map: {
    [k: string]: number;
  };
}
export interface BookmarkCreate {
  section: string;
  ch_pos?: number | null;
  tok_pos?: number | null;
  book_id: number;
  name: string;
  preview?: string | null;
}
export interface BookmarkRename {
  id: number;
  name: string;
}
export interface CollectionBookBase {
  book_id: number;
  collection_id: number;
}
export interface CollectionBookCreate {
  book_id: number;
  collection_id: number;
}
export interface CollectionBookRemove {
  book_id: number;
  collection_id: number;
}
export interface CollectionCreate {
  name: string;
}
export interface CollectionInfoResponse {
  id: number;
  name: string;
}
export interface CollectionRename {
  id: number;
  name: string;
}
export interface CreatorInfoRespone {
  id: number;
  name: string;
}
