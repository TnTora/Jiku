import type { BookRespone } from '$lib/api_types/books.js';

export const load = async ({ params, fetch }) => {
    const res = await fetch(`/api_bridge/books/id/${params.id}`);
	const { book, status_map } = <BookRespone> await res.json();
    // console.log(book);
    console.log(`loaded book ${params.id}`);
	return {book, status_map };
};