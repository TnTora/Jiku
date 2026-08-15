import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
	const response = await resolve(event, {
        preload: ({ type }) => {
            return type === 'js' || type === 'css' || type === 'font';
        }
    });
	return response;
};