<script lang="ts">
	import './layout.css';
	import { browser } from '$app/environment';
	import favicon from '$lib/assets/favicon.svg';
	import { setJikuErrorsContext } from '$lib/utils/context';
	import { setConfirmationPopupContext, setTextInputPopupContext } from '$lib/utils/context';
	import ErrorBox from '$lib/components/ErrorBox.svelte';
	import ConfirmationPopup from '$lib/components/ConfirmationPopup.svelte';
	import TextInputPopup from '$lib/components/TextInputPopup.svelte';
	import type { ConfirmationPopupContext, TextInputPopupContext } from '$lib/utils/context';
	import { setTasksContext } from '$lib/utils/taskEventSource.svelte';
	import { onMount } from 'svelte';
	import TasksMonitor from '$lib/components/TasksMonitor.svelte';


	let { children } = $props();


	// Initialize localStorage default values
	if (browser) {
		let texthooker_presets = localStorage.getItem("texthooker_presets");
		if (!texthooker_presets) {
			const presets_names = ["Default"];
			const default_preset = {
                    websocket_url: "ws://localhost:6677",
                    font_size: 22,
                    vertical: false,
                }
			localStorage.setItem("texthooker_presets", JSON.stringify(presets_names));
			localStorage.setItem("texthooker_preset_Default", JSON.stringify(default_preset));
		}
	}

	// let test_errors = [{short: "test1", details:"test message 1"}, {short: "test2", details:"test message 2"}];
	let errors = $state([]);
	setJikuErrorsContext(errors);
	const task_context = setTasksContext("http://127.0.0.1:8000/books/tasks_events");


	let confirmation_popup: ConfirmationPopupContext = $state({
		show: false,
		text: "",
		onOk: () => { return; },
		onCancel: () => { return; },
	});

	setConfirmationPopupContext(confirmation_popup);

	let text_input_popup: TextInputPopupContext = $state({
		show: false,
		text: "",
		text_input_value: null,
		text_input_default: "",
		onOk: () => {},
		onCancel: () => {},
	});

	setTextInputPopupContext(text_input_popup);

	function resetPopupContexts() {
        text_input_popup.show= false;
        text_input_popup.text = "";
        text_input_popup.text_input_value = null;
		text_input_popup.text_input_default = "";
		text_input_popup.onOk = () => {};
		text_input_popup.onCancel = () => {};

		confirmation_popup.show= false;
        confirmation_popup.text = "";
		confirmation_popup.onOk = () => {};
		confirmation_popup.onCancel = () => {};
    }

	function modalOkWrapper(modalFunc: () => any) {
		return () => {
			let res = modalFunc();
			Promise.resolve(res).then(
				resetPopupContexts
			);
		}
	}

	onMount(() => {
		task_context.connect();
	});

</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<ErrorBox {errors} />

{#if confirmation_popup.show}
	<ConfirmationPopup
		text={confirmation_popup.text}
		onCancel={() => {
			confirmation_popup.onCancel();
			resetPopupContexts();
		}}
		onOk={modalOkWrapper(confirmation_popup.onOk)}
	/>
{/if}

{#if text_input_popup.show}
	<TextInputPopup 
		bind:text_input_value={text_input_popup.text_input_value}
		text_input_default={text_input_popup.text_input_default}
		text={text_input_popup.text}
		onCancel={() => {
			text_input_popup.onCancel();
			resetPopupContexts();
		}}
		onOk={modalOkWrapper(text_input_popup.onOk)}
	/>
{/if}

{#if task_context.tasks.size > 0}
	<TasksMonitor />
{/if}

{@render children()}
