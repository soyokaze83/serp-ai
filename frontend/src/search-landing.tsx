"use client";

import type React from "react";

import { useState, useEffect } from "react";
import { Search, Sparkles, Zap, Shield, Sun, Moon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";

export default function SearchLanding() {
    const [searchQuery, setSearchQuery] = useState("");
    const [isSearching, setIsSearching] = useState(false);
    const [showResults, setShowResults] = useState(false);
    const [showFeatures, setShowFeatures] = useState(false);
    const [showMobileMenu, setShowMobileMenu] = useState(false);
    const [isDarkMode, setIsDarkMode] = useState(false);

    useEffect(() => {
        const savedTheme = localStorage.getItem("theme");
        const prefersDark = window.matchMedia(
            "(prefers-color-scheme: dark)"
        ).matches;

        if (savedTheme === "dark" || (!savedTheme && prefersDark)) {
            setIsDarkMode(true);
            document.documentElement.classList.add("dark");
        }
    }, []);

    const toggleDarkMode = () => {
        const newDarkMode = !isDarkMode;
        setIsDarkMode(newDarkMode);

        if (newDarkMode) {
            document.documentElement.classList.add("dark");
            localStorage.setItem("theme", "dark");
        } else {
            document.documentElement.classList.remove("dark");
            localStorage.setItem("theme", "light");
        }
    };

    useEffect(() => {
        const handleScroll = () => {
            const scrollPosition = window.scrollY;
            const windowHeight = window.innerHeight;
            if (scrollPosition > windowHeight * 0.5) {
                setShowFeatures(true);
            }
        };

        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    const handleSearch = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!searchQuery.trim()) return;

        setIsSearching(true);
        setShowResults(false);

        try {
            // Make API call to search endpoint
            const response = await fetch(
                `https://moral-kiah-soyokaze83-45241348.koyeb.app/search/${encodeURIComponent(
                    searchQuery
                )}`
            );

            if (!response.ok) {
                throw new Error("Search failed");
            }

            const searchResults = await response.json();

            // Navigate to results page with the data
            // Store results in sessionStorage for the results page
            sessionStorage.setItem(
                "searchResults",
                JSON.stringify(searchResults)
            );
            sessionStorage.setItem("searchQuery", searchQuery);

            // Navigate to results page
            window.location.href = "/results";
        } catch (error) {
            console.error("Search error:", error);
            setIsSearching(false);
            // You could add error state handling here
            alert("Search failed. Please try again.");
        }
    };

    const resetSearch = () => {
        setSearchQuery("");
        setIsSearching(false);
        setShowResults(false);
    };

    const scrollToSection = (sectionId: string) => {
        const headerHeight = 80; // Account for fixed header

        if (sectionId === "hero") {
            window.scrollTo({
                top: 0,
                behavior: "smooth",
            });
        } else if (sectionId === "features") {
            // First ensure features section is visible
            setShowFeatures(true);

            // Small delay to allow the section to become visible
            setTimeout(() => {
                const featuresSection =
                    document.getElementById("features-section");
                if (featuresSection) {
                    const elementPosition = featuresSection.offsetTop;
                    const offsetPosition = elementPosition - headerHeight;

                    window.scrollTo({
                        top: offsetPosition,
                        behavior: "smooth",
                    });
                }
            }, 100);
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
            {/* Header - Fixed position */}
            <header
                className={`fixed top-0 left-0 right-0 z-50 transition-colors duration-300 border-b ${
                    isDarkMode
                        ? "bg-slate-900/80 backdrop-blur-md border-slate-700/50"
                        : "bg-white/80 backdrop-blur-md border-slate-200/50"
                }`}
            >
                <div className="max-w-7xl mx-auto flex items-center justify-between px-4 py-4">
                    <div className="flex items-center space-x-2">
                        <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                            <Search className="w-5 h-5 text-white" />
                        </div>
                        <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                            SERP-AI
                        </span>
                    </div>

                    <div className="flex items-center space-x-4">
                        {/* Dark Mode Toggle */}
                        <div className="flex items-center space-x-3">
                            <button
                                onClick={toggleDarkMode}
                                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                                    isDarkMode ? "bg-blue-600" : "bg-slate-300"
                                }`}
                                aria-label="Toggle dark mode"
                            >
                                <span
                                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-300 ease-in-out ${
                                        isDarkMode
                                            ? "translate-x-6"
                                            : "translate-x-1"
                                    }`}
                                />
                                <Sun
                                    className={`absolute left-1 h-3 w-3 text-yellow-500 transition-opacity duration-300 ${
                                        isDarkMode ? "opacity-0" : "opacity-100"
                                    }`}
                                />
                                <Moon
                                    className={`absolute right-1 h-3 w-3 text-slate-200 transition-opacity duration-300 ${
                                        isDarkMode ? "opacity-100" : "opacity-0"
                                    }`}
                                />
                            </button>
                        </div>

                        <button
                            className={`sm:hidden p-2 transition-colors ${
                                isDarkMode
                                    ? "text-slate-300 hover:text-white"
                                    : "text-slate-600 hover:text-slate-900"
                            }`}
                            onClick={() => setShowMobileMenu(!showMobileMenu)}
                        >
                            <svg
                                className="w-6 h-6"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M4 6h16M4 12h16M4 18h16"
                                />
                            </svg>
                        </button>

                        <nav className="hidden sm:flex items-center space-x-8">
                            <button
                                onClick={() => scrollToSection("hero")}
                                className={`transition-colors duration-200 font-medium relative group ${
                                    isDarkMode
                                        ? "text-slate-300 hover:text-white"
                                        : "text-slate-600 hover:text-slate-900"
                                }`}
                            >
                                Search
                                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-600 to-purple-600 transition-all duration-300 group-hover:w-full"></span>
                            </button>
                            <button
                                onClick={() => scrollToSection("features")}
                                className={`transition-colors duration-200 font-medium relative group ${
                                    isDarkMode
                                        ? "text-slate-300 hover:text-white"
                                        : "text-slate-600 hover:text-slate-900"
                                }`}
                            >
                                Features
                                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-600 to-purple-600 transition-all duration-300 group-hover:w-full"></span>
                            </button>
                        </nav>
                    </div>
                </div>
            </header>

            {/* Mobile Menu */}
            {showMobileMenu && (
                <div
                    className={`sm:hidden transition-colors duration-300 border-b ${
                        isDarkMode
                            ? "bg-slate-900/95 backdrop-blur-md border-slate-700/50"
                            : "bg-white/95 backdrop-blur-md border-slate-200/50"
                    }`}
                >
                    <div className="px-4 py-4 space-y-4">
                        <button
                            onClick={() => {
                                scrollToSection("hero");
                                setShowMobileMenu(false);
                            }}
                            className={`block w-full text-left transition-colors duration-200 font-medium py-2 ${
                                isDarkMode
                                    ? "text-slate-300 hover:text-white"
                                    : "text-slate-600 hover:text-slate-900"
                            }`}
                        >
                            Search
                        </button>
                        <button
                            onClick={() => {
                                scrollToSection("features");
                                setShowMobileMenu(false);
                            }}
                            className={`block w-full text-left transition-colors duration-200 font-medium py-2 ${
                                isDarkMode
                                    ? "text-slate-300 hover:text-white"
                                    : "text-slate-600 hover:text-slate-900"
                            }`}
                        >
                            Features
                        </button>
                    </div>
                </div>
            )}

            {/* Hero Section - Full viewport height with perfect centering */}
            <section
                id="hero-section"
                className="min-h-screen flex items-center justify-center px-4 pt-20"
            >
                <div className="w-full max-w-4xl mx-auto">
                    <div className="text-center">
                        {/* Title */}
                        <div className="mb-12">
                            <h1
                                className={`text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold mb-6 leading-tight transition-colors duration-300 ${
                                    isDarkMode ? "text-white" : "text-slate-900"
                                }`}
                            >
                                Search Smarter with{" "}
                                <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                                    AI-Powered
                                </span>{" "}
                                Intelligence
                            </h1>
                            <p
                                className={`text-lg sm:text-xl md:text-2xl max-w-3xl mx-auto leading-relaxed transition-colors duration-300 ${
                                    isDarkMode
                                        ? "text-slate-300"
                                        : "text-slate-600"
                                }`}
                            >
                                Experience the next generation of search with
                                our AI-enhanced engine that delivers accurate,
                                contextual results powered by advanced language
                                models.
                            </p>
                        </div>

                        {/* Search Section - Perfectly centered */}
                        <div className="max-w-3xl mx-auto">
                            <form
                                onSubmit={handleSearch}
                                className="relative mb-8"
                            >
                                <div className="relative">
                                    <Search
                                        className={`absolute left-6 top-1/2 transform -translate-y-1/2 w-6 h-6 ${
                                            isDarkMode
                                                ? "text-slate-400"
                                                : "text-slate-400"
                                        }`}
                                    />
                                    <Input
                                        type="text"
                                        value={searchQuery}
                                        onChange={(e) =>
                                            setSearchQuery(e.target.value)
                                        }
                                        placeholder="Search for anything... Try 'latest AI developments' or 'climate change solutions'"
                                        className={`w-full pl-16 pr-36 py-6 text-xl border-2 rounded-3xl focus:ring-4 transition-all duration-200 shadow-xl hover:shadow-2xl ${
                                            isDarkMode
                                                ? "bg-slate-800 border-slate-600 text-white placeholder-slate-400 focus:border-blue-500 focus:ring-blue-500/20"
                                                : "bg-white border-slate-200 text-slate-900 placeholder-slate-500 focus:border-blue-500 focus:ring-blue-100"
                                        }`}
                                        disabled={isSearching}
                                    />
                                    <Button
                                        type="submit"
                                        disabled={
                                            isSearching || !searchQuery.trim()
                                        }
                                        className="absolute right-3 top-1/2 transform -translate-y-1/2 px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-2xl transition-all duration-200 text-lg font-medium text-white"
                                    >
                                        {isSearching ? (
                                            <div className="flex items-center space-x-2">
                                                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                                <span>Searching</span>
                                            </div>
                                        ) : (
                                            "Search"
                                        )}
                                    </Button>
                                </div>
                            </form>

                            {/* Search Status */}
                            {isSearching && (
                                <Card
                                    className={`shadow-lg transition-colors duration-300 ${
                                        isDarkMode
                                            ? "border-blue-800 bg-blue-900/50"
                                            : "border-blue-200 bg-blue-50"
                                    }`}
                                >
                                    <CardContent className="p-8">
                                        <div className="flex items-center justify-center space-x-4">
                                            <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
                                            <div className="text-center">
                                                <p
                                                    className={`font-medium text-lg ${
                                                        isDarkMode
                                                            ? "text-blue-200"
                                                            : "text-blue-800"
                                                    }`}
                                                >
                                                    Processing your search...
                                                </p>
                                                <p
                                                    className={`mt-2 ${
                                                        isDarkMode
                                                            ? "text-blue-300"
                                                            : "text-blue-600"
                                                    }`}
                                                >
                                                    Our AI is analyzing your
                                                    query and finding the most
                                                    relevant results
                                                </p>
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            )}

                            {/* Results Placeholder */}
                            {showResults && (
                                <Card
                                    className={`shadow-lg transition-colors duration-300 ${
                                        isDarkMode
                                            ? "border-green-800 bg-green-900/50"
                                            : "border-green-200 bg-green-50"
                                    }`}
                                >
                                    <CardContent className="p-8">
                                        <div className="text-center">
                                            <div
                                                className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 ${
                                                    isDarkMode
                                                        ? "bg-green-800"
                                                        : "bg-green-100"
                                                }`}
                                            >
                                                <Sparkles className="w-8 h-8 text-green-600" />
                                            </div>
                                            <p
                                                className={`font-medium text-lg mb-3 ${
                                                    isDarkMode
                                                        ? "text-green-200"
                                                        : "text-green-800"
                                                }`}
                                            >
                                                Search completed!
                                            </p>
                                            <p
                                                className={`mb-6 ${
                                                    isDarkMode
                                                        ? "text-green-300"
                                                        : "text-green-700"
                                                }`}
                                            >
                                                Found relevant results for:{" "}
                                                <span className="font-medium">
                                                    &ldquo;{searchQuery}&rdquo;
                                                </span>
                                            </p>
                                            <Button
                                                onClick={resetSearch}
                                                variant="outline"
                                                className={`transition-colors duration-200 ${
                                                    isDarkMode
                                                        ? "border-green-600 text-green-400 hover:bg-green-800"
                                                        : "border-green-300 text-green-700 hover:bg-green-100"
                                                }`}
                                            >
                                                Search Again
                                            </Button>
                                        </div>
                                    </CardContent>
                                </Card>
                            )}
                        </div>

                        {/* Scroll indicator */}
                        {!showFeatures && (
                            <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
                                <div
                                    className={`flex flex-col items-center ${
                                        isDarkMode
                                            ? "text-slate-500"
                                            : "text-slate-400"
                                    }`}
                                >
                                    <span className="text-sm mb-2">
                                        Scroll to explore
                                    </span>
                                    <div
                                        className={`w-6 h-10 border-2 rounded-full flex justify-center ${
                                            isDarkMode
                                                ? "border-slate-600"
                                                : "border-slate-300"
                                        }`}
                                    >
                                        <div
                                            className={`w-1 h-3 rounded-full mt-2 animate-pulse ${
                                                isDarkMode
                                                    ? "bg-slate-600"
                                                    : "bg-slate-300"
                                            }`}
                                        ></div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </section>

            {/* Features Section - Hidden initially, revealed on scroll */}
            <section
                id="features-section"
                className={`transition-all duration-1000 ease-out ${
                    showFeatures
                        ? "opacity-100 translate-y-0"
                        : "opacity-0 translate-y-20 pointer-events-none"
                }`}
            >
                <div className="min-h-screen flex items-center justify-center px-4 py-20">
                    <div className="max-w-6xl mx-auto">
                        <div className="text-center mb-16">
                            <h2
                                className={`text-4xl md:text-5xl font-bold mb-6 transition-colors duration-300 ${
                                    isDarkMode ? "text-white" : "text-slate-900"
                                }`}
                            >
                                Why Choose SERP-AI?
                            </h2>
                            <p
                                className={`text-xl max-w-3xl mx-auto transition-colors duration-300 ${
                                    isDarkMode
                                        ? "text-slate-300"
                                        : "text-slate-600"
                                }`}
                            >
                                Our advanced search engine combines the power of
                                Elasticsearch with AI-driven result verification
                            </p>
                        </div>

                        <div className="grid md:grid-cols-3 gap-8">
                            {[
                                {
                                    icon: Zap,
                                    title: "Lightning Fast",
                                    description:
                                        "Get instant results powered by optimized Elasticsearch indexing and intelligent caching",
                                    color: "blue",
                                    delay: "delay-0",
                                },
                                {
                                    icon: Sparkles,
                                    title: "AI-Enhanced",
                                    description:
                                        "Every search result is verified and enhanced by our integrated language models for accuracy",
                                    color: "purple",
                                    delay: "delay-200",
                                },
                                {
                                    icon: Shield,
                                    title: "Reliable Results",
                                    description:
                                        "Trust in search results that are fact-checked and contextually relevant to your queries",
                                    color: "green",
                                    delay: "delay-400",
                                },
                            ].map((feature, index) => {
                                const IconComponent = feature.icon;
                                return (
                                    <Card
                                        key={feature.title}
                                        className={`border-0 shadow-xl hover:shadow-2xl transition-all duration-500 hover:-translate-y-2 ${
                                            showFeatures
                                                ? `animate-fade-in-up ${feature.delay}`
                                                : ""
                                        } ${
                                            isDarkMode
                                                ? "bg-slate-800"
                                                : "bg-white"
                                        }`}
                                    >
                                        <CardContent className="p-10 text-center">
                                            <div
                                                className={`w-20 h-20 bg-${
                                                    feature.color
                                                }-100 rounded-3xl flex items-center justify-center mx-auto mb-8 ${
                                                    isDarkMode
                                                        ? `bg-${feature.color}-900/50`
                                                        : `bg-${feature.color}-100`
                                                }`}
                                            >
                                                <IconComponent
                                                    className={`w-10 h-10 text-${feature.color}-600`}
                                                />
                                            </div>
                                            <h3
                                                className={`text-2xl font-semibold mb-4 transition-colors duration-300 ${
                                                    isDarkMode
                                                        ? "text-white"
                                                        : "text-slate-900"
                                                }`}
                                            >
                                                {feature.title}
                                            </h3>
                                            <p
                                                className={`text-lg leading-relaxed transition-colors duration-300 ${
                                                    isDarkMode
                                                        ? "text-slate-300"
                                                        : "text-slate-600"
                                                }`}
                                            >
                                                {feature.description}
                                            </p>
                                        </CardContent>
                                    </Card>
                                );
                            })}
                        </div>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer
                className={`border-t py-12 px-4 transition-colors duration-300 ${
                    isDarkMode
                        ? "border-slate-700 bg-slate-900"
                        : "border-slate-200 bg-white"
                }`}
            >
                <div className="max-w-7xl mx-auto text-center">
                    <div className="flex items-center justify-center space-x-2 mb-4">
                        <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                            <Search className="w-5 h-5 text-white" />
                        </div>
                        <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                            SERP-AI
                        </span>
                    </div>
                    <p
                        className={`transition-colors duration-300 ${
                            isDarkMode ? "text-slate-400" : "text-slate-600"
                        }`}
                    >
                        &copy; 2024 SERP-AI. Powered by advanced search
                        technology and artificial intelligence.
                    </p>
                </div>
            </footer>

            <style jsx>{`
                @keyframes fade-in-up {
                    from {
                        opacity: 0;
                        transform: translateY(30px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }

                .animate-fade-in-up {
                    animation: fade-in-up 0.8s ease-out forwards;
                }

                .delay-0 {
                    animation-delay: 0ms;
                }

                .delay-200 {
                    animation-delay: 200ms;
                }

                .delay-400 {
                    animation-delay: 400ms;
                }
            `}</style>
        </div>
    );
}
