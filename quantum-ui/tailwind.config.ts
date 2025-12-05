import type { Config } from "tailwindcss";

const config: Config = {
    content: [
        "./pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./components/**/*.{js,ts,jsx,tsx,mdx}",
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                // Quantum Deep Space Background
                quantum: {
                    deep: "#0a0e27",
                    darker: "#050711",
                },
                // Primary Quantum Colors
                qpurple: {
                    500: "#7C3AED",
                    600: "#6D28D9",
                    700: "#5B21B6",
                    glow: "#A78BFA",
                },
                qblue: {
                    500: "#3B82F6",
                    600: "#2563EB",
                    700: "#1D4ED8",
                    glow: "#60A5FA",
                },
                qcyan: {
                    500: "#06B6D4",
                    600: "#0891B2",
                    700: "#0E7490",
                    glow: "#22D3EE",
                },
                qpink: {
                    500: "#EC4899",
                    600: "#DB2777",
                    700: "#BE185D",
                    glow: "#F472B6",
                },
                qgreen: {
                    500: "#10B981",
                    600: "#059669",
                    700: "#047857",
                    glow: "#34D399",
                },
            },
            backgroundImage: {
                "quantum-gradient": "linear-gradient(135deg, #0a0e27 0%, #1a1b4b 100%)",
                "quantum-radial": "radial-gradient(circle, rgba(124,58,237,0.1) 0%, transparent 70%)",
            },
            boxShadow: {
                "quantum-glow": "0 0 20px rgba(124, 58, 237, 0.5)",
                "quantum-glow-blue": "0 0 20px rgba(59, 130, 246, 0.5)",
                "quantum-glow-pink": "0 0 20px rgba(236, 72, 153, 0.5)",
                "quantum-glow-green": "0 0 20px rgba(16, 185, 129, 0.5)",
            },
            animation: {
                "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
                "spin-slow": "spin 8s linear infinite",
                "float": "float 6s ease-in-out infinite",
                "glow": "glow 2s ease-in-out infinite alternate",
            },
            keyframes: {
                float: {
                    "0%, 100%": { transform: "translateY(0px)" },
                    "50%": { transform: "translateY(-20px)" },
                },
                glow: {
                    "0%": { boxShadow: "0 0 5px rgba(124, 58, 237, 0.5)" },
                    "100%": { boxShadow: "0 0 20px rgba(124, 58, 237, 1)" },
                },
            },
        },
    },
    plugins: [],
};

export default config;
