import type { PageServerLoad } from './$types';
import { get_all_files } from '$lib/db';

export const load: PageServerLoad = async ({ params }) => {
	const files = get_all_files();
	const file = files.find((file) => file.ident === params.ident && file.file_id === params.file_id);
	const found_file = file ? true : false;

	return {
		ident: params.ident,
		file_id: params.file_id,
		found_file,
		file
	};
};
