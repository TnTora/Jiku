export const load = async ({ params, fetch }) => {
    const res = await fetch(`/api_bridge/books/id/${params.id}`);
	const { book, status_map } = await res.json();
    // console.log(book);
    console.log(`loaded book ${params.id}`);
	return {book, status_map };
};