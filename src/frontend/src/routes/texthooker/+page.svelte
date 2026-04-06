<script lang="ts">
import TexthookerLine from "$lib/components/TexthookerLine.svelte";

let { data } = $props();
let lines = $state(data.lines);
let status_map = $state(data.status_map);
let new_lines: any[] = $state([]);
let ws: WebSocket | null = null;

async function processNewLine(new_line: string) {
    try {
        const res = await fetch("http://127.0.0.1:8000/texthooker/new_line", {
            method: "POST",
            headers: {
                "accept": "application/json",
                "Content-Type": "application/json",
            },
            body: JSON.stringify({text: new_line})
        });

        let { tokens, line_status_map } = await res.json();
        status_map = {...status_map, ...line_status_map};
        return tokens;
    } catch (error) {
        console.error("Error fetching new line: ", error);
        throw error;
    }

}

async function addNewLine() {
    new_lines.push(
        {
            raw: "どうして？彼には何のデメリットもないはずよ。",
            line: processNewLine("どうして？彼には何のデメリットもないはずよ。"),
        })
}
</script>

<!-- last session lines -->
{#each lines as line}
    <TexthookerLine {line} {status_map} />
{/each}

<!-- lines added during current session -->
{#each new_lines as line}
    {#await line.line}
        <p>{line.raw}</p>
    {:then line} 
        <TexthookerLine {line} {status_map} />
    {/await}
{/each}



<button onclick={addNewLine}>Try</button>

<style>
    
</style>

