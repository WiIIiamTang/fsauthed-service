import Database from 'better-sqlite3';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const root_git_repo_drop3 = process.cwd();
const path_to_db = join(root_git_repo_drop3, '..', 'drop1', 'drop1.db');
console.log('path_to_db', path_to_db);

// the db is in ../../../drop1/drop1.db
const db = new Database(path_to_db);
db.pragma('journal_mode = WAL');

export const get_file = (ident: string, file_id: string) => {
	const files = db
		.prepare(
			`
        select
            *
        from
            files
        where
            ident = ? and
            file_id = ?
    `
		)
		.get(ident, file_id);

	return files;
};

export const get_all_files = () => {
	const files = db.prepare(`select * from files`).all();

	return files;
};
