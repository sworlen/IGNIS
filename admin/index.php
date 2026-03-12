<?php

declare(strict_types=1);

$pageTitle = 'IGNIS Admin';
require __DIR__ . '/../includes/header.php';
?>
<section class="mx-auto max-w-3xl">
    <h1 class="mb-3 text-3xl font-bold">Admin editor</h1>
    <p class="mb-6 text-slate-600 dark:text-slate-300">Základní stránka pro správu obsahu (články, release kalendář, uživatelé).</p>

    <div class="grid gap-4 md:grid-cols-2">
        <a href="/admin/editor.php" class="rounded-xl border border-slate-200 bg-white p-5 hover:border-brand-500 dark:border-slate-800 dark:bg-slate-900">
            <h2 class="mb-1 font-semibold">Správa článků</h2>
            <p class="text-sm text-slate-600 dark:text-slate-300">CRUD pro tabulku <code>articles</code>.</p>
        </a>
        <a href="#" class="rounded-xl border border-slate-200 bg-white p-5 hover:border-brand-500 dark:border-slate-800 dark:bg-slate-900">
            <h2 class="mb-1 font-semibold">Release kalendář</h2>
            <p class="text-sm text-slate-600 dark:text-slate-300">CRUD pro tabulku <code>releases</code>.</p>
        </a>
    </div>
</section>

<?php require __DIR__ . '/../includes/footer.php'; ?>
