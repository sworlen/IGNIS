<?php

declare(strict_types=1);

$pageTitle = 'IGNIS | Recenze a release kalendář';
require __DIR__ . '/includes/db.php';
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

$upcomingReleases = [];
if ($pdo instanceof PDO) {
    $statement = $pdo->prepare(
        'SELECT title, platform, release_date, note
         FROM releases
         WHERE release_date >= CURDATE()
         ORDER BY release_date ASC
         LIMIT 10'
    );
    $statement->execute();
    $upcomingReleases = $statement->fetchAll();
}
?>
<div class="grid gap-8 lg:grid-cols-[minmax(0,1fr)_320px]">
    <div>
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
    </div>

    <aside class="h-fit rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
        <h2 class="mb-1 text-xl font-semibold">Kalendář novinek</h2>
        <p class="mb-4 text-sm text-slate-600 dark:text-slate-300">Automaticky plněno cron skriptem z externího API.</p>

        <?php if ($upcomingReleases !== []): ?>
            <ul class="space-y-3">
                <?php foreach ($upcomingReleases as $release): ?>
                    <li class="rounded-lg border border-slate-200 p-3 dark:border-slate-700">
                        <p class="font-semibold"><?= htmlspecialchars($release['title'], ENT_QUOTES, 'UTF-8'); ?></p>
                        <p class="text-xs text-slate-500 dark:text-slate-400">
                            <?= htmlspecialchars((string) ($release['platform'] ?: 'N/A'), ENT_QUOTES, 'UTF-8'); ?>
                            •
                            <?= htmlspecialchars((string) date('d.m.Y', strtotime((string) $release['release_date'])), ENT_QUOTES, 'UTF-8'); ?>
                        </p>
                        <?php if (!empty($release['note'])): ?>
                            <p class="mt-1 text-xs text-slate-600 dark:text-slate-300"><?= htmlspecialchars((string) $release['note'], ENT_QUOTES, 'UTF-8'); ?></p>
                        <?php endif; ?>
                    </li>
                <?php endforeach; ?>
            </ul>
        <?php else: ?>
            <p class="rounded-lg bg-slate-100 p-3 text-sm text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                Zatím nejsou dostupná žádná data. Spusť cron skript <code>cron/fetch_data.php</code> a zkontroluj API klíč.
            </p>
        <?php endif; ?>
    </aside>
</div>

<?php require __DIR__ . '/includes/footer.php'; ?>
