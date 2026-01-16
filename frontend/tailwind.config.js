/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'bg-dark': '#121212',
                'bg-card': '#25262b',
                'border-color': '#3f3f46',
            }
        },
    },
    plugins: [],
}
