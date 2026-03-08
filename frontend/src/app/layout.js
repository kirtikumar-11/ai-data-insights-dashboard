import "./globals.css";

export const metadata = {
  title: "AI Data Insights Dashboard",
  description:
    "Ask natural language questions about your business data and receive answers, charts, and AI-powered insights.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body>{children}</body>
    </html>
  );
}
