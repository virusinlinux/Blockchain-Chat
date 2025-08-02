<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blockchain Chat: The Future of Messaging</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #003f5c;
            color: #ffffff;
        }
        .chart-container {
            position: relative;
            width: 100%;
            max-width: 450px;
            margin-left: auto;
            margin-right: auto;
            height: 300px;
            max-height: 400px;
        }
        @media (min-width: 768px) {
            .chart-container {
                height: 350px;
            }
        }
        .flow-arrow {
            position: relative;
            width: 100%;
            height: 2rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .flow-arrow::after {
            content: '▼';
            font-size: 2rem;
            color: #ffa600;
        }
         .timeline-item::before {
            content: '';
            position: absolute;
            left: -0.6rem;
            top: 0.5rem;
            width: 1.2rem;
            height: 1.2rem;
            border-radius: 50%;
            background-color: #ffa600;
            border: 3px solid #003f5c;
        }
    </style>
</head>
<body class="antialiased">

    <div class="container mx-auto p-4 md:p-8">

        <header class="text-center my-12 md:my-20">
            <h1 class="text-4xl md:text-6xl font-black tracking-tight text-white uppercase">Blockchain <span style="color: #ffa600;">Chat</span></h1>
            <p class="mt-4 text-lg md:text-xl text-gray-300 max-w-3xl mx-auto">A revolutionary decentralized messaging app for secure, serverless, and offline communication powered by Blockchain and Bluetooth.</p>
        </header>

        <main>
            <section id="features" class="my-16">
                <h2 class="text-3xl font-bold text-center mb-12">Core Pillars of Trust & Functionality</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
                    
                    <div class="bg-white/10 rounded-xl p-6 backdrop-blur-sm transform hover:scale-105 transition-transform duration-300">
                        <div class="text-5xl mb-4" style="color: #ef5675;">🔐</div>
                        <h3 class="text-xl font-bold mb-2">Security & Privacy</h3>
                        <p class="text-gray-300">With end-to-end encryption and blockchain verification, your conversations are immutable, tamper-proof, and truly private.</p>
                    </div>

                    <div class="bg-white/10 rounded-xl p-6 backdrop-blur-sm transform hover:scale-105 transition-transform duration-300">
                        <div class="text-5xl mb-4" style="color: #bc5090;">📱</div>
                        <h3 class="text-xl font-bold mb-2">Core Functionality</h3>
                        <p class="text-gray-300">Communicate entirely offline via a Bluetooth mesh network. Share files, create group chats, and message without an internet connection.</p>
                    </div>

                    <div class="bg-white/10 rounded-xl p-6 backdrop-blur-sm transform hover:scale-105 transition-transform duration-300">
                        <div class="text-5xl mb-4" style="color: #7a5195;">🎨</div>
                        <h3 class="text-xl font-bold mb-2">User Experience</h3>
                        <p class="text-gray-300">A clean, cross-platform UI with simple QR code pairing and real-time status indicators makes secure messaging effortless.</p>
                    </div>
                </div>
            </section>

            <section id="tech-stack" class="my-24">
                <div class="bg-white/10 rounded-xl p-8 backdrop-blur-sm">
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
                        <div class="text-center lg:text-left">
                            <h2 class="text-3xl font-bold mb-4">The Technology Powering the Chat</h2>
                            <p class="text-gray-300 mb-4">Blockchain Chat is built on a robust stack of modern, open-source technologies. Each component is carefully selected to ensure security, performance, and cross-platform compatibility without relying on central servers.</p>
                            <p class="text-gray-300">The frontend is driven by Kivy for a unified look across devices, while Python's asyncio and the Bleak library manage the complex asynchronous Bluetooth communications that form the app's core.</p>
                        </div>
                        <div>
                            <div class="chart-container">
                                <canvas id="techStackChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <section id="how-it-works" class="my-24">
                <h2 class="text-3xl font-bold text-center mb-12">A Secure Messaging Journey</h2>
                <p class="text-center text-gray-300 max-w-3xl mx-auto mb-12">The magic of Blockchain Chat lies in its simple yet powerful process that turns nearby devices into a secure, self-healing network. Here’s how a message travels from sender to receiver without ever touching the internet.</p>
                <div class="flex flex-col items-center">
                    
                    <div class="w-full max-w-md bg-white/10 rounded-xl p-6 text-center shadow-lg mb-4">
                        <div class="text-2xl font-bold mb-2" style="color: #ff764a;">1. Device Discovery</div>
                        <p class="text-gray-200">The app continuously scans for nearby devices running Blockchain Chat using Bluetooth Low Energy (BLE).</p>
                    </div>
                    <div class="flow-arrow"></div>
                    
                    <div class="w-full max-w-md bg-white/10 rounded-xl p-6 text-center shadow-lg mb-4">
                        <div class="text-2xl font-bold mb-2" style="color: #ef5675;">2. Secure Pairing</div>
                        <p class="text-gray-200">Devices exchange public keys via QR codes to establish a secure, encrypted channel for all future communication.</p>
                    </div>
                    <div class="flow-arrow"></div>

                    <div class="w-full max-w-md bg-white/10 rounded-xl p-6 text-center shadow-lg mb-4">
                        <div class="text-2xl font-bold mb-2" style="color: #bc5090;">3. Blockchain Messaging</div>
                        <p class="text-gray-200">Each message is signed, encrypted, and added as a new block to a distributed, device-local blockchain, ensuring integrity.</p>
                    </div>
                    <div class="flow-arrow"></div>

                    <div class="w-full max-w-md bg-white/10 rounded-xl p-6 text-center shadow-lg">
                        <div class="text-2xl font-bold mb-2" style="color: #7a5195;">4. Mesh Networking</div>
                        <p class="text-gray-200">If the recipient is out of direct range, messages can securely hop between trusted intermediate devices to reach their final destination.</p>
                    </div>
                </div>
            </section>
            
            <section id="roadmap" class="my-24">
                <h2 class="text-3xl font-bold text-center mb-12">The Future is Decentralized</h2>
                 <div class="max-w-3xl mx-auto">
                    <div class="relative pl-8 border-l-2 border-white/20">
                        
                        <div class="mb-8 timeline-item">
                            <h3 class="text-xl font-bold" style="color: #ffa600;">Complete File Sharing</h3>
                            <p class="text-gray-300">Finalize the implementation for robust and secure sharing of any file type.</p>
                        </div>
                        
                        <div class="mb-8 timeline-item">
                            <h3 class="text-xl font-bold" style="color: #ff764a;">Voice & Video Messaging</h3>
                            <p class="text-gray-300">Introduce real-time, encrypted voice and video calls over the Bluetooth mesh.</p>
                        </div>
                        
                        <div class="mb-8 timeline-item">
                            <h3 class="text-xl font-bold" style="color: #ef5675;">Smart Contracts</h3>
                            <p class="text-gray-300">Integrate blockchain-based smart contracts for advanced features like scheduled messages or automated actions.</p>
                        </div>

                        <div class="mb-8 timeline-item">
                            <h3 class="text-xl font-bold" style="color: #bc5090;">Wallet Integration</h3>
                            <p class="text-gray-300">Allow users to send and receive cryptocurrency transactions directly within the chat interface.</p>
                        </div>

                        <div class="timeline-item">
                            <h3 class="text-xl font-bold" style="color: #7a5195;">Dark Mode & More</h3>
                            <p class="text-gray-300">Implement a full dark mode, message search, and chat backup/restore functionality.</p>
                        </div>
                    </div>
                </div>
            </section>

             <section id="contribute" class="my-24 text-center">
                <h2 class="text-3xl font-bold mb-4">Help Build the Future</h2>
                <p class="text-gray-300 max-w-2xl mx-auto mb-8">Blockchain Chat is an open-source project, and we welcome contributors. Help us build a more private and resilient communication tool for everyone.</p>
                <a href="#" class="inline-block bg-yellow-500 text-gray-900 font-bold py-3 px-8 rounded-lg text-lg hover:bg-yellow-400 transition-colors duration-300" style="background-color: #ffa600;">View on GitHub</a>
            </section>

        </main>

        <footer class="text-center py-8 mt-12 border-t border-white/10">
            <p class="text-gray-400">&copy; 2025 Blockchain Chat. Licensed under the MIT License.</p>
        </footer>

    </div>

    <script>
        function wrapLabel(str, maxWidth) {
            if (str.length <= maxWidth) {
                return str;
            }
            const words = str.split(' ');
            const lines = [];
            let currentLine = '';
            for (const word of words) {
                if ((currentLine + word).length > maxWidth) {
                    lines.push(currentLine.trim());
                    currentLine = '';
                }
                currentLine += word + ' ';
            }
            lines.push(currentLine.trim());
            return lines.filter(line => line.length > 0);
        }

        const techStackCtx = document.getElementById('techStackChart').getContext('2d');
        const techStackChart = new Chart(techStackCtx, {
            type: 'doughnut',
            data: {
                labels: ['Python & Asyncio', 'Kivy (UI)', 'Bleak (Bluetooth)', 'Cryptography', 'Custom Blockchain'],
                datasets: [{
                    label: 'Technology Stack',
                    data: [30, 25, 20, 15, 10],
                    backgroundColor: [
                        '#7a5195',
                        '#bc5090',
                        '#ef5675',
                        '#ff764a',
                        '#ffa600'
                    ],
                    borderColor: '#003f5c',
                    borderWidth: 4,
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#ffffff',
                            font: {
                                size: 14
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            title: function(tooltipItems) {
                                const item = tooltipItems[0];
                                let label = item.chart.data.labels[item.dataIndex];
                                if (Array.isArray(label)) {
                                  return label.join(' ');
                                } else {
                                  return label;
                                }
                            }
                        }
                    }
                },
                cutout: '60%'
            }
        });
    </script>
</body>
</html>
