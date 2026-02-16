import { Container, Header } from '@/components/ui';
import { MetadataWorkspace } from '@/components/MetadataWorkspace';

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col bg-[#f9fafb] font-[family-name:var(--font-inter)]">
      <Header />

      <main className="mx-auto flex w-full max-w-6xl flex-1 flex-col px-6 py-12">
        <Container>
          <MetadataWorkspace />
        </Container>
      </main>

      {/* Footer */}
      <footer className="border-t border-[#e5e7eb] bg-white px-6 py-3 text-center text-sm text-[#9ca3af]">
        &copy; {new Date().getFullYear()} Metadata Generator &mdash; PoC
      </footer>
    </div>
  );
}
