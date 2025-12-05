/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./components/**/*.{js,ts,jsx,tsx,mdx}",
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                // Pure Black Background
                quantum: {
                    black: "#000000",
                    dark: "#0a0a0a",
                    darker: "#050505",
                },
                // Electric Cyan (Primary)
                qcyan: {
                    400: "#00F0FF",
                    500: "#00D9FF",
                    600: "#00C2E0",
                    glow: "#00F0FF",
                },
                // Neon Green (Secondary)
                qgreen: {
                    400: "#00FF88",
                    500: "#00FF41",
                    600: "#00DD35",
                    glow: "#00FF88",
                },
                // Hot Orange (Accent)
                qorange: {
                    400: "#FF8C42",
                    500: "#FF6B35",
                    600: "#FF4500",
                    glow: "#FF8C42",
                },
                // Electric Blue (Support)
                qblue: {
                    400: "#00BFFF",
                    500: "#0099FF",
                    600: "#0077CC",
                    glow: "#00BFFF",
                },
            },
            backgroundImage: {
                "quantum-gradient": "linear-gradient(135deg, #000000 0%, #0a0a0a 100%)",
                "cyber-lines": "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0, 217, 255, 0.03) 2px, rgba(0, 217, 255, 0.03) 4px)",
            },
            boxShadow: {
                "quantum-glow": "0 0 30px rgba(0, 217, 255, 0.6), 0 0 60px rgba(0, 217, 255, 0.3)",
                "quantum-glow-green": "0 0 30px rgba(0, 255, 65, 0.6), 0 0 60px rgba(0, 255, 65, 0.3)",
                "quantum-glow-orange": "0 0 30px rgba(255, 107, 53, 0.6), 0 0 60px rgba(255, 107, 53, 0.3)",
                "neon-cyan": "0 0 20px rgba(0, 240, 255, 0.8)",
                "neon-green": "0 0 20px rgba(0, 255, 136, 0.8)",
            },
            animation: {
                "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
                "spin-slow": "spin 8s linear infinite",
                "float": "float 6s ease-in-out infinite",
                "glow": "glow 2s ease-in-out infinite alternate",
                "scan": "scan 8s linear infinite",
            },
            keyframes: {
                float: {
                    "0%, 100%": { transform: "translateY(0px)" },
                    "50%": { transform: "translateY(-20px)" },
                },
                glow: {
                    "0%": { boxShadow: "0 0 10px rgba(0, 217, 255, 0.5)" },
                    "100%": { boxShadow: "0 0 30px rgba(0, 217, 255, 1)" },
                },
                scan: {
                    "0%": { transform: "translateY(-100%)" },
                    "100%": { transform: "translateY(100%)" },
                },
            },
        },
    },
    plugins: [],
};
