"use client";

import { useState, useEffect } from "react";
import {
    Search,
    ArrowLeft,
    ExternalLink,
    Calendar,
    Users,
    BookOpen,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface SearchResult {
    _index: string;
    _id: string;
    _score: number;
    _source: {
        citekey: string;
        entry_type: string;
        title: string;
        abstract: string;
        text: string;
        booktitle?: string;
        year: number;
        month?: string;
        pages?: string;
        address?: string;
        publisher?: string;
        url?: string;
        authors: string[];
        editors?: string[];
    };
    cross_encoder_score: number;
}

interface SearchResponse {
    query: string;
    initial_hits_count: number;
    reranked_hits: SearchResult[];
}

export default function SearchResults() {
    const [searchResults, setSearchResults] = useState<SearchResponse | null>(
        null
    );
    const [searchQuery, setSearchQuery] = useState("");
    const [isDarkMode, setIsDarkMode] = useState(false);
    const [summary, setSummary] = useState("");
    const [isSummarizing, setIsSummarizing] = useState(false);

    useEffect(() => {
        const darkMode = document.documentElement.classList.contains("dark");
        setIsDarkMode(darkMode);

        const results = sessionStorage.getItem("searchResults");
        const query = sessionStorage.getItem("searchQuery");

        if (results && query) {
            setSearchResults(JSON.parse(results));
            setSearchQuery(query);
        } else {
            window.location.href = "/";
        }
    }, []);

    const goBack = () => {
        window.location.href = "/";
    };

    const formatAuthors = (authors: string[]) => {
        if (!authors) return "Unknown Authors";

        if (authors.length <= 2) {
            return authors.join(" and ");
        }
        return `${authors[0]} et al.`;
    };

    const truncateText = (text: string, maxLength: number) => {
        if (!text) return "No description available.";

        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + "...";
    };

    if (!searchResults) {
        return (
            <div
                className={`min-h-screen flex items-center justify-center ${
                    isDarkMode ? "bg-slate-900" : "bg-slate-50"
                }`}
            >
                <div className="text-center">
                    <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                    <p className={isDarkMode ? "text-white" : "text-slate-900"}>
                        Loading results...
                    </p>
                </div>
            </div>
        );
    }

    const handleSummarizeResults = async () => {
        if (!searchResults || !searchQuery) return;

        setIsSummarizing(true);
        setSummary("");

        try {
            const response = await fetch(
                `https://moral-kiah-soyokaze83-45241348.koyeb.app/summarize_documents_stream`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        query: searchQuery,
                        documents: searchResults.reranked_hits,
                    }),
                }
            );

            if (!response.ok) {
                throw new Error(`Summarization failed: ${response.statusText}`);
            }

            if (!response.body) {
                throw new Error("Response body is null");
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let done = false;

            while (!done) {
                const { value, done: readerDone } = await reader.read();
                done = readerDone;
                if (value) {
                    const chunk = decoder.decode(value, { stream: true });
                    setSummary((prev) => prev + chunk);
                }
            }
        } catch (error) {
            console.error("Summarization error:", error);
            setSummary("Failed to generate summary. Please try again.");
        } finally {
            setIsSummarizing(false);
        }
    };

    return (
        <div
            className={`min-h-screen transition-colors duration-300 ${
                isDarkMode
                    ? "bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900"
                    : "bg-gradient-to-br from-slate-50 via-white to-slate-100"
            }`}
        >
            {/* Header */}
            <header
                className={`sticky top-0 z-50 transition-colors duration-300 border-b ${
                    isDarkMode
                        ? "bg-slate-900/80 backdrop-blur-md border-slate-700/50"
                        : "bg-white/80 backdrop-blur-md border-slate-200/50"
                }`}
            >
                <div className="max-w-7xl mx-auto flex items-center justify-between px-4 py-4">
                    <div className="flex items-center space-x-4">
                        <Button
                            onClick={goBack}
                            variant="ghost"
                            size="sm"
                            className={`${
                                isDarkMode
                                    ? "text-slate-300 hover:text-white"
                                    : "text-slate-600 hover:text-slate-900"
                            }`}
                        >
                            <ArrowLeft className="w-4 h-4 mr-2" />
                            Back to Search
                        </Button>
                        <div className="flex items-center space-x-2">
                            <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                                <Search className="w-5 h-5 text-white" />
                            </div>
                            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                                SERP-AI
                            </span>
                        </div>
                    </div>
                </div>
            </header>

            {/* Results Content */}
            <main className="max-w-6xl mx-auto px-4 py-8">
                {/* Search Summary */}
                <div className="mb-8">
                    <h1
                        className={`text-3xl font-bold mb-2 ${
                            isDarkMode ? "text-white" : "text-slate-900"
                        }`}
                    >
                        Search Results for &ldquo;{searchQuery}&rdquo;
                    </h1>
                    <p
                        className={`text-lg mb-2 ${
                            isDarkMode ? "text-slate-300" : "text-slate-600"
                        }`}
                    >
                        Found {searchResults.initial_hits_count} results (
                        {searchResults.reranked_hits.length} shown)
                    </p>
                    <Button onClick={handleSummarizeResults} disabled={isSummarizing} className="cursor-pointer">
                        {isSummarizing ? "Summarizing..." : "✨ Generate Summary"}
                    </Button>
                </div>

                <div className="space-y-6">

                    {summary && (
                        <Card className="mt-6 mb-8">
                            <CardHeader><CardTitle>AI Summary</CardTitle></CardHeader>
                            <CardContent><pre className="whitespace-pre-wrap">{summary}</pre></CardContent>
                        </Card>
                    )}

                    {searchResults.reranked_hits.map((result, index) => (
                        <Card
                            key={result._id}
                            className={`transition-all duration-300 hover:shadow-xl hover:-translate-y-1 ${
                                isDarkMode
                                    ? "bg-slate-800 border-slate-700"
                                    : "bg-white border-slate-200"
                            }`}
                        >
                            <CardHeader>
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <CardTitle
                                            className={`text-xl mb-2 leading-tight ${
                                                isDarkMode
                                                    ? "text-white"
                                                    : "text-slate-900"
                                            }`}
                                        >
                                            {result._source.title}
                                        </CardTitle>
                                        <div className="flex flex-wrap items-center gap-2 mb-3">
                                            <Badge
                                                variant="secondary"
                                                className="text-xs"
                                            >
                                                <Calendar className="w-3 h-3 mr-1" />
                                                {result._source.year}
                                            </Badge>
                                            <Badge
                                                variant="outline"
                                                className="text-xs"
                                            >
                                                <Users className="w-3 h-3 mr-1" />
                                                {formatAuthors(
                                                    result._source.authors
                                                )}
                                            </Badge>
                                            {result._source.booktitle && (
                                                <Badge
                                                    variant="outline"
                                                    className="text-xs"
                                                >
                                                    <BookOpen className="w-3 h-3 mr-1" />
                                                    {truncateText(
                                                        result._source
                                                            .booktitle,
                                                        40
                                                    )}
                                                </Badge>
                                            )}
                                        </div>
                                    </div>
                                    <div className="flex flex-col items-end space-y-2 ml-4">
                                        <Badge className="bg-blue-100 text-blue-800 text-xs">
                                            Score: {result._score.toFixed(2)}
                                        </Badge>
                                        {result._source.url && (
                                            <Button
                                                size="sm"
                                                variant="outline"
                                                onClick={() =>
                                                    window.open(
                                                        result._source.url,
                                                        "_blank"
                                                    )
                                                }
                                                className="text-xs"
                                            >
                                                <ExternalLink className="w-3 h-3 mr-1" />
                                                View Paper
                                            </Button>
                                        )}
                                    </div>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <p
                                    className={`text-sm leading-relaxed ${
                                        isDarkMode
                                            ? "text-slate-300"
                                            : "text-slate-600"
                                    }`}
                                >
                                    {truncateText(result._source.abstract, 400)}
                                </p>

                                {/* Additional Details */}
                                <div
                                    className={`mt-4 pt-4 border-t text-xs space-y-1 ${
                                        isDarkMode
                                            ? "border-slate-700 text-slate-400"
                                            : "border-slate-200 text-slate-500"
                                    }`}
                                >
                                    {result._source.publisher && (
                                        <p>
                                            <strong>Publisher:</strong>{" "}
                                            {result._source.publisher}
                                        </p>
                                    )}
                                    {result._source.address && (
                                        <p>
                                            <strong>Location:</strong>{" "}
                                            {result._source.address}
                                        </p>
                                    )}
                                    {result._source.pages && (
                                        <p>
                                            <strong>Pages:</strong>{" "}
                                            {result._source.pages}
                                        </p>
                                    )}
                                    <p>
                                        <strong>Document ID:</strong>{" "}
                                        {result._source.citekey}
                                    </p>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>

                {/* No Results Message */}
                {searchResults.reranked_hits.length === 0 && (
                    <div className="text-center py-12">
                        <div
                            className={`text-6xl mb-4 ${
                                isDarkMode ? "text-slate-600" : "text-slate-300"
                            }`}
                        >
                            🔍
                        </div>
                        <h2
                            className={`text-2xl font-bold mb-2 ${
                                isDarkMode ? "text-white" : "text-slate-900"
                            }`}
                        >
                            No results found
                        </h2>
                        <p
                            className={`text-lg mb-6 ${
                                isDarkMode ? "text-slate-300" : "text-slate-600"
                            }`}
                        >
                            Try adjusting your search terms or check for typos.
                        </p>
                        <Button
                            onClick={goBack}
                            className="bg-gradient-to-r from-blue-600 to-purple-600 text-white"
                        >
                            Try Another Search
                        </Button>
                    </div>
                )}
            </main>
        </div>
    );
}
