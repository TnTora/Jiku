import type { BookInfoResponse, CollectionInfoResponse, CreatorInfoRespone } from '$lib/api_types/books.js';

export const load = async ({ url, fetch }) => {
    let res = await fetch(`/api_bridge/books/books_info?${url.searchParams.toString()}`);
    const books: BookInfoResponse[] = await res.json();
    res = await fetch(`/api_bridge/books/collections`);
	const collections: CollectionInfoResponse[] = await res.json();
    res = await fetch(`/api_bridge/books/creators`);
	const creators: CreatorInfoRespone[] = await res.json();
    console.log(books, collections, creators);
	return {books, collections, creators};
};