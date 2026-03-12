<?php

declare(strict_types=1);

$pageTitle = 'IGNIS Admin | Editor článku';
require __DIR__ . '/../includes/header.php';
?>
<section class="mx-auto max-w-5xl">
    <div class="mb-6 flex items-start justify-between gap-4">
        <div>
            <h1 class="text-3xl font-bold">Editor článku</h1>
            <p class="mt-2 text-slate-600 dark:text-slate-300">Vytvoř nebo uprav článek přes WYSIWYG editor, přidej klady/zápory a nastav procentuální verdikt.</p>
        </div>
        <a href="/admin/index.php" class="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800">Zpět do adminu</a>
    </div>

    <form action="#" method="post" enctype="multipart/form-data" class="space-y-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="grid gap-4 md:grid-cols-2">
            <div>
                <label for="title" class="mb-2 block text-sm font-medium">Titulek</label>
                <input type="text" id="title" name="title" required class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none ring-brand-500/40 focus:ring dark:border-slate-700 dark:bg-slate-950">
            </div>
            <div>
                <label for="category" class="mb-2 block text-sm font-medium">Kategorie</label>
                <input type="text" id="category" name="category" required class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none ring-brand-500/40 focus:ring dark:border-slate-700 dark:bg-slate-950">
            </div>
        </div>

        <div>
            <label for="content" class="mb-2 block text-sm font-medium">Obsah článku</label>
            <textarea id="content" name="content"></textarea>
            <p class="mt-2 text-xs text-slate-500 dark:text-slate-400">Editor podporuje vkládání obrázků a YouTube videí (embed).</p>
        </div>

        <div class="grid gap-4 md:grid-cols-2">
            <div>
                <label for="rating_pros" class="mb-2 block text-sm font-medium">Klady</label>
                <textarea id="rating_pros" name="rating_pros" rows="4" placeholder="Např. Výborný příběh&#10;Skvělý soundtrack" class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none ring-brand-500/40 focus:ring dark:border-slate-700 dark:bg-slate-950"></textarea>
            </div>
            <div>
                <label for="rating_cons" class="mb-2 block text-sm font-medium">Zápory</label>
                <textarea id="rating_cons" name="rating_cons" rows="4" placeholder="Např. Slabší optimalizace&#10;Občasné bugy" class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none ring-brand-500/40 focus:ring dark:border-slate-700 dark:bg-slate-950"></textarea>
            </div>
        </div>

        <div>
            <label for="rating_score" class="mb-2 block text-sm font-medium">Procentuální hodnocení (Verdikt): <span id="rating_score_value">75%</span></label>
            <input type="range" id="rating_score" name="rating_score" min="0" max="100" value="75" class="w-full accent-brand-600">
        </div>

        <div>
            <label for="main_image" class="mb-2 block text-sm font-medium">Hlavní obrázek</label>
            <input type="file" id="main_image" name="main_image" accept="image/*" class="block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-950">
            <p class="mt-2 text-xs text-slate-500 dark:text-slate-400">Pro TinyMCE upload je připraven endpoint <code>/admin/upload_image.php</code>.</p>
        </div>

        <button type="submit" class="rounded-lg bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-brand-500">Uložit článek</button>
    </form>
</section>

<script src="https://cdn.tiny.cloud/1/no-api-key/tinymce/6/tinymce.min.js" referrerpolicy="origin"></script>
<script>
    tinymce.init({
        selector: '#content',
        height: 500,
        menubar: true,
        plugins: 'advlist autolink lists link image charmap preview anchor searchreplace visualblocks code fullscreen insertdatetime media table wordcount help',
        toolbar: 'undo redo | blocks | bold italic underline | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image media | code fullscreen preview',
        images_upload_url: '/admin/upload_image.php',
        automatic_uploads: true,
        images_reuse_filename: false,
        image_title: true,
        file_picker_types: 'image media',
        media_live_embeds: true,
        content_style: 'body { font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif; font-size:16px }',
    });

    const ratingInput = document.getElementById('rating_score');
    const ratingValue = document.getElementById('rating_score_value');

    ratingInput.addEventListener('input', () => {
        ratingValue.textContent = `${ratingInput.value}%`;
    });
</script>

<?php require __DIR__ . '/../includes/footer.php'; ?>
