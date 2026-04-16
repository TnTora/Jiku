<script lang="ts">
    import { getTextHookerOptionsContext } from "../../routes/texthooker/context";
    let { line, status_map, delete_func } = $props()
    let options = getTextHookerOptionsContext();

</script>

<div class="relative flex items-center">
    <p class="my-1 py-1 px-5 whitespace-pre-wrap" style="font-size: {options.font_size}px;">
        {#each line.tokens as word}
            {#if word.inflection in status_map}
                <span class="relative status-underline {status_map[word.inflection]}">{word.inflection}</span><wbr>
            {:else if (word.pos !== "PUNCT" && word.pos !== "SPACE")}
                <span class="relative status-underline unknown">{word.inflection}</span>
            {:else}
                {word.inflection}
            {/if}
    
        {/each}
    </p>
    <button onclick={delete_func} class="mr-4 ml-auto hover:text-sky-700 active:text-sky-500 hover:cursor-pointer">X</button>
</div>

<style>
    span {
        word-break: keep-all;
        overflow-wrap: anywhere;
    }
</style>