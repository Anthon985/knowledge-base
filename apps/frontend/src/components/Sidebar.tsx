import { NavLink } from "react-router-dom"
import { cn } from "@/lib/utils"
import { LayoutDashboard, Upload, Search, MessageSquare, FileText, Database } from "lucide-react"

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "仪表盘" },
  { to: "/upload", icon: Upload, label: "上传文档" },
  { to: "/search", icon: Search, label: "全文检索" },
  { to: "/chat", icon: MessageSquare, label: "智能问答" },
  { to: "/documents", icon: FileText, label: "文档管理" },
]

export function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-64 flex-col gradient-sidebar border-r border-sidebar-border">
      <div className="flex h-16 items-center gap-3 px-6 border-b border-sidebar-border">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg gradient-primary">
          <Database className="h-5 w-5 text-primary-foreground" />
        </div>
        <div>
          <h1 className="text-base font-bold text-sidebar-accent-foreground">智库</h1>
          <p className="text-xs text-sidebar-foreground/60">智能文档知识库</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-4">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-sidebar-accent text-sidebar-accent-foreground"
                  : "text-sidebar-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground"
              )
            }
          >
            <item.icon className="h-4.5 w-4.5 shrink-0" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-sidebar-border p-4">
        <div className="rounded-lg bg-sidebar-accent/30 px-3 py-3">
          <p className="text-xs font-medium text-sidebar-accent-foreground">GitOps 部署</p>
          <p className="mt-1 text-xs text-sidebar-foreground/60">ArgoCD + K8s</p>
        </div>
      </div>
    </aside>
  )
}