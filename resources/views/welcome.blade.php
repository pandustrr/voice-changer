<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}" class="dark">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>VoiceCloner AI - Premium Voice Transformation</title>

    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">

    @vite(['resources/css/app.css', 'resources/js/app.js'])

    <style>
        :root {
            --primary: #6366f1;
            --secondary: #a855f7;
            --accent: #22d3ee;
        }

        body {
            font-family: 'Outfit', sans-serif;
            background: #030712;
            background-image:
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0, transparent 50%),
                radial-gradient(at 100% 0%, rgba(168, 85, 247, 0.15) 0, transparent 50%);
            min-height: 100vh;
            color: #f3f4f6;
        }

        .glass {
            background: rgba(17, 24, 39, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }

        .text-gradient {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            transition: all 0.3s ease;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px -5px rgba(99, 102, 241, 0.5);
        }

        .animate-pulse-slow {
            animation: pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }

        @keyframes pulse {

            0%,
            100% {
                opacity: 1;
            }

            50% {
                opacity: .5;
            }
        }
    </style>
</head>

<body class="antialiased selection:bg-indigo-500/30">
    <div class="fixed top-0 left-0 w-full h-full pointer-events-none z-[-1] overflow-hidden">
        <div class="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-500/10 blur-[120px] rounded-full"></div>
        <div class="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-500/10 blur-[120px] rounded-full"></div>
    </div>

    <div id="app" class="max-w-4xl mx-auto px-6 py-16">
        <header class="text-center mb-16 relative">
            <div class="inline-block px-4 py-1.5 mb-6 rounded-full border border-indigo-500/30 bg-indigo-500/5 text-indigo-400 text-sm font-medium tracking-wide">
                ✨ AI-Powered Voice Cloning
            </div>
            <h1 class="text-6xl font-extrabold mb-6 tracking-tight leading-tight">
                Change Your Voice <br>
                <span class="text-gradient uppercase italic">Like Magic</span>
            </h1>
            <p class="text-gray-400 text-xl max-w-2xl mx-auto leading-relaxed">
                Record your voice once, and let AI generate any speech in your unique tone. Perfect for creators, podcasters, and storytellers.
            </p>
        </header>

        <main class="grid gap-10">
            <!-- Step 1: Record -->
            <section class="glass rounded-[32px] p-10 relative overflow-hidden group">
                <div class="relative z-10">
                    <div class="flex items-center gap-5 mb-8">
                        <div class="w-12 h-12 rounded-2xl bg-indigo-500/20 flex items-center justify-center text-indigo-400 font-bold text-xl border border-indigo-500/20">1</div>
                        <div>
                            <h2 class="text-2xl font-bold">Voice Initialization</h2>
                            <p class="text-gray-500 text-sm italic">Filmora Style - High Fidelity Capture</p>
                        </div>
                    </div>

                    <div class="flex flex-col items-center justify-center py-12 border-2 border-dashed border-white/5 rounded-3xl bg-white/[0.02] transition-all hover:bg-white/[0.04] hover:border-indigo-500/30 group/record">
                        <div id="recordBtn" class="relative cursor-pointer group-active/record:scale-95 transition-transform duration-200">
                            <div class="absolute -inset-4 bg-red-500/20 rounded-full blur-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
                            <div class="w-24 h-24 rounded-full bg-red-500 flex items-center justify-center shadow-2xl shadow-red-500/40 relative z-10 transition-colors" id="recordBtnCircle">
                                <svg id="micIcon" xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                                </svg>
                                <div id="stopIcon" class="hidden w-8 h-8 bg-white rounded-lg"></div>
                            </div>
                        </div>
                        <p id="recordStatus" class="mt-8 text-gray-400 font-medium tracking-wide">Press to start recording (5-10 sec)</p>

                        <div id="previewContainer" class="hidden w-full max-w-md mt-8 space-y-4">
                            <div class="flex items-center gap-3 px-4 py-3 bg-white/5 rounded-xl border border-white/10">
                                <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                                <span class="text-sm font-medium">Reference Audio Captured</span>
                            </div>
                            <audio id="audioPreview" controls class="w-full opacity-80"></audio>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Step 2: Input Text -->
            <section class="glass rounded-[32px] p-10 opacity-40 grayscale cursor-not-allowed transition-all duration-700 relative" id="step2">
                <div class="flex items-center gap-5 mb-8">
                    <div class="w-12 h-12 rounded-2xl bg-purple-500/20 flex items-center justify-center text-purple-400 font-bold text-xl border border-purple-500/20">2</div>
                    <div>
                        <h2 class="text-2xl font-bold">Script Creation</h2>
                        <p class="text-gray-500 text-sm italic">Transform text into your voice</p>
                    </div>
                </div>

                <div class="relative">
                    <textarea id="textInput" disabled class="w-full bg-black/40 border border-white/10 rounded-2xl p-8 text-white text-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/50 placeholder:text-gray-600 transition-all resize-none shadow-inner" rows="4" placeholder="Enter the text you want your voice to speak..."></textarea>
                    <div class="absolute bottom-4 right-4 text-xs text-gray-600 font-mono tracking-tighter">AI ENGINE READY</div>
                </div>

                <button id="generateBtn" disabled class="btn-primary mt-8 w-full py-5 rounded-2xl font-bold text-xl tracking-wide flex items-center justify-center gap-3 group">
                    <span>Generate AI Voice</span>
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                </button>
            </section>

            <!-- Step 3: Result -->
            <section class="glass rounded-[32px] p-10 hidden border-green-500/20 bg-green-500/5 scale-95 opacity-0 transition-all duration-500" id="resultSection">
                <div class="flex items-center justify-between mb-8">
                    <div class="flex items-center gap-5">
                        <div class="w-12 h-12 rounded-2xl bg-green-500/20 flex items-center justify-center text-green-400 font-bold text-xl border border-green-500/20">3</div>
                        <div>
                            <h2 class="text-2xl font-bold">Master Output</h2>
                            <p class="text-gray-500 text-sm italic">High Definition WAV Generated</p>
                        </div>
                    </div>
                    <div class="px-3 py-1 bg-green-500/10 text-green-400 text-xs font-bold rounded-md border border-green-500/20">SUCCESS</div>
                </div>

                <div class="p-8 bg-black/40 rounded-2xl border border-white/5 space-y-8">
                    <div class="space-y-4">
                        <label class="text-xs uppercase tracking-widest text-gray-500 font-bold">Playback</label>
                        <audio id="finalAudio" controls class="w-full"></audio>
                    </div>

                    <div class="flex gap-4">
                        <a id="downloadBtn" href="#" download="cloned-voice.wav" class="flex-1 py-4 bg-white/10 hover:bg-white/20 rounded-xl font-bold flex items-center justify-center gap-2 border border-white/10 transition-colors">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                            </svg>
                            Download High-Res
                        </a>
                        <button onclick="window.location.reload()" class="w-16 h-14 bg-white/5 hover:bg-red-500/10 hover:text-red-400 rounded-xl border border-white/10 flex items-center justify-center transition-all group">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 group-hover:rotate-180 transition-transform duration-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                            </svg>
                        </button>
                    </div>
                </div>
            </section>
        </main>

        <footer class="mt-24 text-center">
            <div class="h-px w-full bg-gradient-to-r from-transparent via-white/10 to-transparent mb-8"></div>
            <p class="text-gray-500 text-sm font-medium tracking-widest uppercase">
                &copy; {{ date('Y') }} VoiceCloner AI &bull; Created for Premium Creators
            </p>
        </footer>
    </div>

    <!-- JS Logic -->
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            let mediaRecorder;
            let audioChunks = [];
            let audioBlob;

            const recordBtn = document.getElementById('recordBtn');
            const recordBtnCircle = document.getElementById('recordBtnCircle');
            const micIcon = document.getElementById('micIcon');
            const stopIcon = document.getElementById('stopIcon');
            const recordStatus = document.getElementById('recordStatus');
            const previewContainer = document.getElementById('previewContainer');
            const audioPreview = document.getElementById('audioPreview');

            const step2 = document.getElementById('step2');
            const textInput = document.getElementById('textInput');
            const generateBtn = document.getElementById('generateBtn');

            const resultSection = document.getElementById('resultSection');
            const finalAudio = document.getElementById('finalAudio');

            recordBtn.addEventListener('click', async () => {
                if (!mediaRecorder || mediaRecorder.state === 'inactive') {
                    try {
                        const stream = await navigator.mediaDevices.getUserMedia({
                            audio: true
                        });
                        mediaRecorder = new MediaRecorder(stream);
                        audioChunks = [];

                        mediaRecorder.ondataavailable = (event) => {
                            audioChunks.push(event.data);
                        };

                        mediaRecorder.onstop = () => {
                            audioBlob = new Blob(audioChunks, {
                                type: 'audio/wav'
                            });
                            const audioUrl = URL.createObjectURL(audioBlob);
                            audioPreview.src = audioUrl;
                            previewContainer.classList.remove('hidden');

                            // Enable step 2 with animation
                            step2.classList.remove('opacity-40', 'grayscale', 'cursor-not-allowed');
                            textInput.disabled = false;
                            generateBtn.disabled = false;

                            recordStatus.textContent = "Initialization Complete";
                            recordStatus.classList.add('text-green-400');
                        };

                        mediaRecorder.start();
                        micIcon.classList.add('hidden');
                        stopIcon.classList.remove('hidden');
                        recordBtnCircle.classList.replace('bg-red-500', 'bg-gray-800');
                        recordBtnCircle.classList.add('animate-pulse');
                        recordStatus.textContent = "Capturing Voice Profile...";
                    } catch (err) {
                        alert("Microphone access denied. Please allow microphone to use this app.");
                    }
                } else {
                    mediaRecorder.stop();
                    micIcon.classList.remove('hidden');
                    stopIcon.classList.add('hidden');
                    recordBtnCircle.classList.replace('bg-gray-800', 'bg-red-500');
                    recordBtnCircle.classList.remove('animate-pulse');
                }
            });

            generateBtn.addEventListener('click', async () => {
                const text = textInput.value;
                if (!text || !audioBlob) return;

                generateBtn.disabled = true;
                generateBtn.innerHTML = `
                    <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Synthesizing Voice...</span>
                `;

                const formData = new FormData();
                formData.append('audio', audioBlob, 'reference.wav');
                formData.append('text', text);

                try {
                    const response = await fetch('/api/clone-voice', {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                        }
                    });

                    if (response.ok) {
                        const blob = await response.blob();
                        const url = URL.createObjectURL(blob);
                        finalAudio.src = url;

                        resultSection.classList.remove('hidden');
                        setTimeout(() => {
                            resultSection.classList.remove('scale-95', 'opacity-0');
                        }, 50);

                        document.getElementById('downloadBtn').href = url;
                        resultSection.scrollIntoView({
                            behavior: 'smooth'
                        });
                    } else {
                        const errData = await response.json();
                        alert('Error: ' + (errData.error || 'Unknown error'));
                    }
                } catch (err) {
                    console.error(err);
                    alert('Bridge failure: Cannot reach AI synthesis engine.');
                } finally {
                    generateBtn.disabled = false;
                    generateBtn.innerHTML = `
                        <span>Generate AI Voice</span>
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                        </svg>
                    `;
                }
            });
        });
    </script>
</body>

</html>