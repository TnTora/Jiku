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
	import { setTasksContext, setSyncTaskContext } from '$lib/utils/taskEventSource.svelte';
	import { onMount } from 'svelte';
	import TasksMonitor from '$lib/components/TasksMonitor.svelte';
	import CenteredPopup from '$lib/components/CenteredPopup.svelte';


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

	const sync_task_context = setSyncTaskContext("http://127.0.0.1:8000/anki/sync_status");


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

	async function stopSync() {
		sync_task_context.sync_task = null;
		const res = await fetch("http://127.0.0.1:8000/anki/stop_morphemes_sync", {
			method: "PUT"
		});
	}

	onMount(() => {
		task_context.connect();
		sync_task_context.connect();
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

{#if sync_task_context.sync_task}
	<CenteredPopup>
		<div class="flex flex-col items-center">
			<p>Syncing morphs with Anki</p>
			<p>Status: {sync_task_context.sync_task.status}</p>
			<p>Analizying: {sync_task_context.sync_task.progress.current_rule_name}</p>
			<p>Rule: {sync_task_context.sync_task.progress.current_rule}/{sync_task_context.sync_task.progress.total_rules}</p>
			<p>Note: {sync_task_context.sync_task.progress.current_note}/{sync_task_context.sync_task.progress.total_notes}</p>
			<svg class="w-10 h-10" fill="#6C89FF" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
				<g>
					<circle cx="12" cy="2.5" r="1.5" opacity=".14"/>
					<circle cx="16.75" cy="3.77" r="1.5" opacity=".29"/>
					<circle cx="20.23" cy="7.25" r="1.5" opacity=".43"/>
					<circle cx="21.50" cy="12.00" r="1.5" opacity=".57"/>
					<circle cx="20.23" cy="16.75" r="1.5" opacity=".71"/>
					<circle cx="16.75" cy="20.23" r="1.5" opacity=".86"/>
					<circle cx="12" cy="21.5" r="1.5"/>
					<animateTransform attributeName="transform" type="rotate" calcMode="discrete" dur="0.75s" values="0 12 12;30 12 12;60 12 12;90 12 12;120 12 12;150 12 12;180 12 12;210 12 12;240 12 12;270 12 12;300 12 12;330 12 12;360 12 12" repeatCount="indefinite"/>
				</g>
			</svg>
		</div>
		<button
			class="py-1 px-2 bg-neutral-600 hover:bg-neutral-700 active:bg-neutral-500 rounded-md cursor-pointer"
			onclick={stopSync}>
			Stop
		</button>
	</CenteredPopup>
{/if}

{@render children()}
