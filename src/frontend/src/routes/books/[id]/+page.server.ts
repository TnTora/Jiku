export const load = async ({ params }) => {
    const res = await fetch(`http://127.0.0.1:8000/books/id/${params.id}`);
	const book = await res.json();
    console.log(book);
	return {book};
};