<?php

declare(strict_types=1);

$pageTitle = $pageTitle ?? 'IGNIS';
?>
<!DOCTYPE html>
<html lang="cs" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($pageTitle, ENT_QUOTES, 'UTF-8'); ?></title>
    <script>
        (() => {
            const savedTheme = localStorage.getItem('theme');
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
        })();
    </script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        brand: {
                            500: '#6366f1',
                            600: '#4f46e5'
                        }
                    }
                }
            }
        };
    </script>
    <link rel="stylesheet" href="/assets/css/styles.css">
</head>
<body class="bg-slate-100 text-slate-900 transition-colors duration-300 dark:bg-slate-950 dark:text-slate-100">
<header class="border-b border-slate-200 bg-white/90 backdrop-blur dark:border-slate-800 dark:bg-slate-900/70">
    <div class="mx-auto flex w-full max-w-6xl items-center justify-between px-4 py-4">
        <a href="/index.php" class="text-xl font-bold tracking-tight text-brand-600 dark:text-brand-500">IGNIS</a>
        <nav class="flex items-center gap-3">
            <a href="/index.php" class="rounded-md px-3 py-2 text-sm font-medium hover:bg-slate-100 dark:hover:bg-slate-800">Domů</a>
            <a href="/admin/index.php" class="rounded-md px-3 py-2 text-sm font-medium hover:bg-slate-100 dark:hover:bg-slate-800">Admin</a>
            <button type="button" id="theme-toggle" class="rounded-md border border-slate-300 px-3 py-2 text-sm font-medium dark:border-slate-600">
                Přepnout režim
            </button>
        </nav>
    </div>
</header>
<main class="mx-auto w-full max-w-6xl px-4 py-10">
