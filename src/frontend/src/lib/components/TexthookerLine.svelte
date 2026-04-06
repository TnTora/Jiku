<script lang="ts">
    let { line, status_map } = $props()
    import { tick } from 'svelte';

	$effect.pre(() => {
		console.log('the component is about to update');
		tick().then(() => {
			console.log(`${line[0].inflection} just updated`);
		});
	});
</script>

<p>
    {#each line as word}
        {#if word.inflection in status_map}
            <span class="{status_map[word.inflection]}">{word.inflection}</span>
        {:else }
            {word.inflection}
        {/if}

    {/each}
</p>

<style>

</style>