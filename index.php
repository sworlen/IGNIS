<?php

declare(strict_types=1);

$pageTitle = 'IGNIS | Přehled článků';
require __DIR__ . '/includes/db.php';
require __DIR__ . '/includes/header.php';

$articles = [];

if ($pdo instanceof PDO) {
    $statement = $pdo->query(
        'SELECT id, title, content, image, category, rating_score, created_at
         FROM articles
         ORDER BY created_at DESC
         LIMIT 12'
    );
    $articles = $statement->fetchAll();
}
?>
<section class="mb-8 rounded-2xl bg-gradient-to-r from-brand-600 to-indigo-500 p-8 text-white shadow-xl">
    <p class="mb-2 text-sm uppercase tracking-[0.2em] text-indigo-100">IGNIS</p>
    <h1 class="mb-3 text-3xl font-bold md:text-4xl">Články a recenze</h1>
    <p class="max-w-2xl text-indigo-100">Moderní homepage v čistém PHP + Tailwind CSS, napojená na MySQL databázi.</p>
</section>

<section class="mb-8">
    <?php if ($pdo instanceof PDO): ?>
        <div class="rounded-xl border border-emerald-300 bg-emerald-50 px-4 py-3 text-emerald-700 dark:border-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300">
            Připojení k Ignis DB úspěšné
        </div>
    <?php else: ?>
        <div class="rounded-xl border border-rose-300 bg-rose-50 px-4 py-3 text-rose-700 dark:border-rose-700 dark:bg-rose-900/30 dark:text-rose-300">
            Chyba připojení: <?= htmlspecialchars((string) $dbError, ENT_QUOTES, 'UTF-8'); ?>
        </div>
    <?php endif; ?>
</section>

<section>
    <div class="mb-4 flex items-center justify-between">
        <h2 class="text-2xl font-semibold">Nejnovější články</h2>
        <span class="rounded-full bg-slate-200 px-3 py-1 text-xs font-semibold dark:bg-slate-800">Tabulka: articles</span>
    </div>

    <?php if ($articles !== []): ?>
        <div class="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            <?php foreach ($articles as $article): ?>
                <article class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-md dark:border-slate-800 dark:bg-slate-900">
                    <?php if (!empty($article['image'])): ?>
                        <img src="<?= htmlspecialchars((string) $article['image'], ENT_QUOTES, 'UTF-8'); ?>" alt="<?= htmlspecialchars((string) $article['title'], ENT_QUOTES, 'UTF-8'); ?>" class="h-44 w-full object-cover">
                    <?php else: ?>
                        <div class="flex h-44 items-center justify-center bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400">Bez obrázku</div>
                    <?php endif; ?>

                    <div class="p-4">
                        <div class="mb-2 flex items-center justify-between text-xs">
                            <span class="rounded-md bg-brand-500/15 px-2 py-1 font-medium text-brand-600 dark:text-brand-400">
                                <?= htmlspecialchars((string) $article['category'], ENT_QUOTES, 'UTF-8'); ?>
                            </span>
                            <span class="font-semibold text-emerald-600 dark:text-emerald-400"><?= number_format((float) $article['rating_score'], 1); ?>%</span>
                        </div>
                        <h3 class="mb-2 text-lg font-semibold"><?= htmlspecialchars((string) $article['title'], ENT_QUOTES, 'UTF-8'); ?></h3>
                        <p class="mb-3 text-sm text-slate-600 dark:text-slate-300">
                            <?= htmlspecialchars(strip_tags((string) $article['content']), ENT_QUOTES, 'UTF-8'); ?>
                        </p>
                        <p class="text-xs text-slate-500 dark:text-slate-400">
                            Publikováno: <?= htmlspecialchars((string) date('d.m.Y H:i', strtotime((string) $article['created_at'])), ENT_QUOTES, 'UTF-8'); ?>
                        </p>
                    </div>
                </article>
            <?php endforeach; ?>
        </div>
    <?php else: ?>
        <p class="rounded-lg bg-slate-100 p-4 text-sm text-slate-600 dark:bg-slate-800 dark:text-slate-300">
            Zatím nejsou v tabulce <code>articles</code> žádná data.
        </p>
    <?php endif; ?>
</section>

<?php require __DIR__ . '/includes/footer.php'; ?>
