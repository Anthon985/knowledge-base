import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Search, FileText, Loader2 } from "lucide-react"
import { searchDocuments, type SearchHit } from "@/lib/api"

export function SearchPage() {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<SearchHit[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return
    setIsSearching(true)
    setHasSearched(true)
    try {
      const res = await searchDocuments(query.trim())
      setResults(res.hits)
    } catch {
      setResults([])
    } finally {
      setIsSearching(false)
    }
  }

  const highlightText = (text: string, q: string) => {
    if (!q.trim()) return text
    const regex = new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi")
    const parts = text.split(regex)
    return parts.map((part, i) =>
      regex.test(part) ? (
        <mark key={i} className="bg-accent text-accent-foreground rounded px-0.5">
          {part}
        </mark>
      ) : (
        part
      )
    )
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">全文检索</h2>
        <p className="text-muted-foreground mt-1">在知识库中搜索文档内容</p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="输入关键词搜索知识库内容..."
            className="h-11 w-full rounded-lg border bg-card pl-10 pr-4 text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-ring placeholder:text-muted-foreground"
          />
        </div>
        <Button type="submit" disabled={isSearching || !query.trim()}>
          {isSearching ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Search className="mr-2 h-4 w-4" />}
          搜索
        </Button>
      </form>

      {isSearching && (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      )}

      {!isSearching && hasSearched && results.length === 0 && (
        <div className="py-16 text-center text-muted-foreground">
          <Search className="mx-auto h-12 w-12 mb-4 opacity-20" />
          <p className="text-base font-medium">未找到相关内容</p>
          <p className="text-sm mt-1">尝试使用不同的关键词搜索</p>
        </div>
      )}

      {!isSearching && results.length > 0 && (
        <div className="space-y-3">
          <p className="text-sm text-muted-foreground">
            找到 <span className="font-medium text-foreground">{results.length}</span> 条相关结果
          </p>
          {results.map((hit, idx) => (
            <Card key={`${hit.document_id}_${hit.chunk_index}`} className="animate-fade-in" style={{ animationDelay: `${idx * 50}ms` }}>
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-accent text-xs font-bold text-accent-foreground">
                    {idx + 1}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <FileText className="h-3.5 w-3.5 text-primary" />
                      <span className="text-xs font-medium text-primary">{hit.filename}</span>
                      <span className="text-xs text-muted-foreground">· 相关度 {(hit.score * 100).toFixed(0)}%</span>
                    </div>
                    <p className="text-sm leading-relaxed text-foreground/80">{highlightText(hit.content, query)}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}