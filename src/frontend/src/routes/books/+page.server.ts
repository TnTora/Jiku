import type { BookInfoResponse, CollectionInfoResponse, CreatorInfoRespone } from '$lib/api_types/books.js';

export const load = async ({ url, fetch }) => {
    let res = await fetch(`/api_bridge/books/books_info?${url.searchParams.toString()}`);
    let books: BookInfoResponse[] = await res.json();
    res = await fetch(`/api_bridge/books/collections`);
	let collections: CollectionInfoResponse[] = await res.json();
    res = await fetch(`/api_bridge/books/creators`);
	let creators: CreatorInfoRespone[] = await res.json();
    console.log(books, collections, creators);
	return {books, collections, creators};
};