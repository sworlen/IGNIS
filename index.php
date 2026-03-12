<?php

declare(strict_types=1);

$pageTitle = 'IGNIS | Recenze a release kalendář';
require __DIR__ . '/includes/header.php';

$featuredArticles = [
    [
        'title' => 'IGNIS Review #1',
        'category' => 'Akce',
        'content' => 'Ukázkový článek s moderním layoutem. Data můžeš následně tahat přímo z MySQL.',
        'rating' => 8.9,
    ],
    [
        'title' => 'IGNIS Review #2',
        'category' => 'RPG',
        'content' => 'Druhá ukázka karty pro rychlé otestování struktury webu a stylu v dark modu.',
        'rating' => 9.1,
    ],
];
?>
<section class="mb-10 rounded-2xl bg-gradient-to-r from-brand-600 to-indigo-500 p-8 text-white shadow-xl">
    <p class="mb-2 text-sm uppercase tracking-[0.2em] text-indigo-100">Čisté PHP + Tailwind</p>
    <h1 class="mb-3 text-3xl font-bold md:text-4xl">Základní kostra webu je připravená</h1>
    <p class="max-w-2xl text-indigo-100">
        Máš připravený frontend, základní includes, admin sekci i SQL skript pro databázi users, articles a releases.
    </p>
</section>

<section class="mb-12">
    <div class="mb-4 flex items-center justify-between">
        <h2 class="text-2xl font-semibold">Poslední recenze</h2>
        <span class="rounded-full bg-slate-200 px-3 py-1 text-xs font-semibold dark:bg-slate-800">Demo data</span>
    </div>

    <div class="grid gap-5 md:grid-cols-2">
        <?php foreach ($featuredArticles as $article): ?>
            <article class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md dark:border-slate-800 dark:bg-slate-900">
                <div class="mb-3 flex items-center justify-between">
                    <span class="rounded-md bg-brand-500/15 px-2 py-1 text-xs font-medium text-brand-600 dark:text-brand-400">
                        <?= htmlspecialchars($article['category'], ENT_QUOTES, 'UTF-8'); ?>
                    </span>
                    <span class="text-sm font-semibold text-emerald-600 dark:text-emerald-400"><?= number_format($article['rating'], 1); ?>/10</span>
                </div>
                <h3 class="mb-2 text-lg font-semibold"><?= htmlspecialchars($article['title'], ENT_QUOTES, 'UTF-8'); ?></h3>
                <p class="text-sm text-slate-600 dark:text-slate-300"><?= htmlspecialchars($article['content'], ENT_QUOTES, 'UTF-8'); ?></p>
            </article>
        <?php endforeach; ?>
    </div>
</section>

<section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900">
    <h2 class="mb-2 text-xl font-semibold">Automatický release kalendář</h2>
    <p class="text-sm text-slate-600 dark:text-slate-300">
        Data pro release kalendář ukládej do tabulky <code class="rounded bg-slate-100 px-1 py-0.5 dark:bg-slate-800">releases</code>.
        Následně můžeš jednoduše vypsat nadcházející tituly podle <code class="rounded bg-slate-100 px-1 py-0.5 dark:bg-slate-800">release_date</code>.
    </p>
</section>

<?php require __DIR__ . '/includes/footer.php'; ?>
