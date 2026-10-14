import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";
import { AppShell } from "@/layouts/AppShell";

export const metadata = {
  title: "Social Security Lab",
  description: "CSC 489 educational social media security capstone"
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <AppShell>{children}</AppShell>
        </AuthProvider>
      </body>
    </html>
  );
}
