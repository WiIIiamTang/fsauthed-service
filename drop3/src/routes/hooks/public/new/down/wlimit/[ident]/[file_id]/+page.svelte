<script lang="ts">
	import { goto, invalidateAll } from '$app/navigation';
    import type { PageData } from './$types';
    import dayjs from 'dayjs';
    import utc from 'dayjs/plugin/utc';
    dayjs.extend(utc);

    export let data: PageData;

    const handleClickDownload = async () => {
        goto(`/hooks/public/down/wlimit/${data.file.ident}/${data.file.file_id}/d`);
        await new Promise(resolve => setTimeout(resolve, 2000));
        invalidateAll();
    }
</script>

<div class="bg-gradient-to-b from-sky-300 to-sky-700 min-h-screen w-full flex flex-col items-center">
    {#if data.found_file}
    <div class="w-1/2">
        {#if data.file.uses_left <= 0}
        <h1 class="text-slate-800 text-4xl leading-relaxed cursor-default select-none text-center">No uses left for this file.</h1>
        {:else if dayjs.utc().isAfter(dayjs.utc(data.file.expires_at))}
        <h1 class="text-slate-800 text-4xl leading-relaxed cursor-default select-none text-center">This file has expired.</h1>
        {:else}
        <h1 class="text-slate-800 text-4xl leading-relaxed cursor-default select-none text-center">"<code>{data.file.ident_user_friendly}</code>" is sending over a file:</h1>
        <div class="bg-slate-700 px-4 py-4 my-2 rounded-md shadow-lg border-slate-800 border-2 flex flex-col gap-2">
            <code class="text-white text-center">{data.file.path}</code>
            <button type="button" on:click={handleClickDownload} class="bg-gradient-to-r from-emerald-300 to-emerald-600 hover:from-green-200 hover:to-green-400 rounded-md py-2 font-light">Download</button>
        </div>
        <h3 class="text-zinc-800 font-thin text-center select-none">Click on the button above to download it. One use will be consumed.</h3>
        <div class="my-8 bg-gradient-to-br from-amber-200 to-rose-300 px-2 py-2 rounded-md shadow-xl">
            <h2 class="text-3xl mb-2">Info:</h2>
            <ul>
                <li>
                    <span class="text-slate-800 font-bold">Original request size:</span>
                    <span class="text-slate-800">{data.file.file_size}B</span>
                </li>
                <li>
                    <span class="text-slate-800 font-bold">Uses left:</span>
                    <span class="text-slate-800">{data.file.uses_left}</span>
                </li>
                <li>
                    <span class="text-slate-800 font-bold">Created at:</span>
                    <span class="text-slate-800">{data.file.created_at}</span>
                </li>
                <li>
                    <span class="text-slate-800 font-bold">Expires at:</span>
                    <span class="text-slate-800">{data.file.expires_at}</span>
                </li>
                <li>
                    <span class="text-slate-800 font-bold">From user:</span>
                    <span class="text-slate-800">{data.file.ident_user_friendly}</span>
                </li>
                <li>
                    <span class="text-slate-800 font-bold">File:</span>
                    <span class="text-slate-800">{data.file.path}</span>
                </li>
            </ul>
        </div>
        {/if}
    </div>
    {:else}
    <div>
        <h1 class="text-slate-800 text-8xl leading-relaxed cursor-default select-none text-center">File not found</h1>
    </div>
    {/if}
</div>