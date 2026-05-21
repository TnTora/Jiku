export const load = async ({ params }) => {
    const res = await fetch(`http://127.0.0.1:8000/books/id/${params.id}`);
	const { book, status_map } = await res.json();
    // console.log(book);
    console.log(`loaded book ${params.id}`);
	return {book, status_map };
};