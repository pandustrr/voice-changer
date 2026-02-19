<!DOCTYPE html>
<html lang="en" class="dark">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI System Debugger — VoiceCloner</title>
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    @vite(['resources/css/app.css', 'resources/js/app.js'])
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #020617;
            color: #f1f5f9;
        }

        .debug-card {
            background-color: #0f172a;
            border: 1px solid #1e293b;
            border-radius: 12px;
        }

        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }

        .bg-success {
            background-color: #10b981;
            box-shadow: 0 0 10px rgba(16, 185, 129, 0.4);
        }

        .bg-error {
            background-color: #ef4444;
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.4);
        }

        .bg-warning {
            background-color: #f59e0b;
        }
    </style>
</head>

<body class="p-6 md:p-12">
    <div class="max-w-4xl mx-auto">
        <header class="flex justify-between items-center mb-12">
            <div>
                <h1 class="text-3xl font-bold tracking-tight">System Debugger</h1>
                <p class="text-slate-400 mt-1">Verify AI services and storage health.</p>
            </div>
            <a href="/" class="text-sm font-medium text-indigo-400 hover:text-indigo-300">Back to App &rarr;</a>
        </header>

        <div class="grid gap-6">
            <!-- 1. AI API CONNECTION -->
            <div class="debug-card p-6">
                <div class="flex justify-between items-center mb-6">
                    <h2 class="font-bold flex items-center gap-2 text-lg">
                        <svg class="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                        Local AI Server Status
                    </h2>
                    <div id="ai-status-badge" class="flex items-center gap-2 px-3 py-1 bg-slate-800 rounded-full text-xs font-bold">
                        <div class="status-dot bg-warning"></div>
                        CHECKING
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="bg-slate-950 p-4 rounded-lg border border-slate-800">
                        <div class="text-xs text-slate-500 font-bold mb-1 tracking-widest">ENDPOINT</div>
                        <code id="ai-endpoint" class="text-indigo-300 text-sm italic">{{ env('AI_TRAINING_URL', 'http://127.0.0.1:5000') }}</code>
                    </div>
                    <div class="bg-slate-950 p-4 rounded-lg border border-slate-800">
                        <div class="text-xs text-slate-500 font-bold mb-1 tracking-widest">ENGINE NAME</div>
                        <span id="ai-engine-name" class="text-sm text-slate-300 italic">Finding...</span>
                    </div>
                </div>
            </div>

            <!-- 2. STORAGE STATUS -->
            <div class="debug-card p-6">
                <h2 class="font-bold flex items-center gap-2 text-lg mb-6">
                    <svg class="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 1.105 4.477 2 10 2s10-.895 10-2V7M4 7c0 1.105 4.477 2 10 2s10-.895 10-2M4 7c0-1.105 4.477-2 10-2s10 .895 10 2m0 10c0 1.105-4.477 2-10 2s-10-.895-10-2" />
                    </svg>
                    Filesystem Configuration
                </h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="bg-indigo-500/10 p-4 rounded-lg border border-indigo-500/20">
                        <div class="text-xs text-indigo-400 font-bold mb-1">ACTIVE DISK</div>
                        <div class="text-lg font-bold text-white uppercase">{{ env('FILESYSTEM_DISK', 'local') }}</div>
                    </div>
                    <div class="bg-slate-950 p-4 rounded-lg border border-slate-800">
                        <div class="text-xs text-slate-500 font-bold mb-1">STORAGE PATH</div>
                        <div class="text-sm text-slate-300 truncate">/storage/app/public</div>
                    </div>
                    <div class="bg-slate-950 p-4 rounded-lg border border-slate-800">
                        <div class="text-xs text-slate-500 font-bold mb-1">CLOUD ACCESS</div>
                        <div class="text-sm {{ env('AWS_ACCESS_KEY_ID') ? 'text-emerald-400 font-bold' : 'text-slate-600' }}">
                            {{ env('AWS_ACCESS_KEY_ID') ? 'CONFIGURED' : 'NOT SET' }}
                        </div>
                    </div>
                </div>
            </div>

            <!-- 3. AI SERVICES (SaaS) -->
            <div class="debug-card p-6">
                <h2 class="font-bold flex items-center gap-2 text-lg mb-6">
                    <svg class="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                    External SaaS Services
                </h2>
                <div class="space-y-4">
                    <div class="flex justify-between items-center p-4 bg-slate-950 rounded-xl border border-slate-800">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 bg-indigo-500/10 rounded-lg flex items-center justify-center font-bold text-xs text-indigo-400">MP</div>
                            <div>
                                <div class="text-sm font-bold">Modal.com</div>
                                <div class="text-xs text-slate-500">Auto-scale Inference</div>
                            </div>
                        </div>
                        <div class="text-xs font-bold {{ env('MODAL_TOKEN_ID') ? 'text-emerald-500' : 'text-slate-600' }}">
                            {{ env('MODAL_TOKEN_ID') ? 'READY' : 'OFFLINE' }}
                        </div>
                    </div>

                    <div class="flex justify-between items-center p-4 bg-slate-950 rounded-xl border border-slate-800">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 bg-purple-500/10 rounded-lg flex items-center justify-center font-bold text-xs text-purple-400">RP</div>
                            <div>
                                <div class="text-sm font-bold">RunPod</div>
                                <div class="text-xs text-slate-500">Fine-tuning Worker</div>
                            </div>
                        </div>
                        <div class="text-xs font-bold {{ env('RUNPOD_API_KEY') ? 'text-emerald-500' : 'text-slate-600' }}">
                            {{ env('RUNPOD_API_KEY') ? 'READY' : 'OFFLINE' }}
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <button onclick="checkHealth()" class="mt-8 w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 rounded-xl transition-all shadow-lg hover:shadow-indigo-500/20">
            Refresh Health Check
        </button>
    </div>

    <script>
        async function checkHealth() {
            const badge = document.getElementById('ai-status-badge');
            const engineText = document.getElementById('ai-engine-name');
            const endpoint = document.getElementById('ai-endpoint').textContent;

            badge.innerHTML = '<div class="status-dot bg-warning"></div> CHECKING';
            engineText.textContent = "Connecting...";

            try {
                // We check the Python backend /health endpoint we created earlier
                const response = await fetch('/api/engine-status');
                const data = await response.json();

                const xttsAvailable = data.engines.xtts.available;

                if (xttsAvailable) {
                    badge.innerHTML = '<div class="status-dot bg-success animate-pulse"></div> ONLINE';
                    badge.classList.replace('bg-slate-800', 'bg-emerald-500/10');
                    engineText.textContent = data.engines.xtts.details.engine || "XTTS v2 Active";
                } else {
                    throw new Error();
                }
            } catch (err) {
                badge.innerHTML = '<div class="status-dot bg-error"></div> OFFLINE';
                badge.classList.replace('bg-slate-800', 'bg-red-500/10');
                engineText.textContent = "Server Unreachable";
            }
        }

        // Run on load
        window.onload = checkHealth;
    </script>
</body>

</html>