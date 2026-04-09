<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { setContext } from "svelte";
	import ErrorBox from '$lib/components/ErrorBox.svelte';

	let { children } = $props();
	// let test_errors = [{short: "test1", details:"test message 1"}, {short: "test2", details:"test message 2"}];
	let errors = $state([]);
	setContext("errors", errors);

</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<ErrorBox {errors} />
{@render children()}
