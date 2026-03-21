import { ChatSidebar } from "@/components/chat-sidebar";

export default function ChatLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-[calc(100vh-3rem)] -m-6">
      <ChatSidebar />
      <div className="flex-1 flex flex-col p-4">{children}</div>
    </div>
  );
}
