"""Adapt the existing reference driver to observed stock SDK error semantics and safe lifecycle."""
import hashlib


def build_driver(source):
    changes = [
        ('\t\treturn -EINVAL;\n\t}\n\n\tif (g_func_array[func_cmd])',
         '\t\treturn -EOPNOTSUPP;\n\t}\n\n\tif (g_func_array[func_cmd])'),
        ('\treturn -EINVAL;\n}\n\nstatic const struct file_operations',
         '\treturn -EOPNOTSUPP;\n}\n\nstatic const struct file_operations'),
        ('''\terr = misc_register(&access_tokenid_device);
\tif (err < 0) {
\t\tpr_err("access_tokenid register failed\\n");
\t\treturn err;
\t}

\tg_cache = kmem_cache_create("access_token_node", sizeof(struct token_perm_node), 0, SLAB_HWCACHE_ALIGN, NULL);
\tif (g_cache == NULL) {
\t\tpr_err("access_tokenid kmem_cache create failed\\n");
\t\treturn -ENOMEM;
\t}''', '''\t/* Allocate backing storage before publishing the device. */
\tg_cache = kmem_cache_create("access_token_node", sizeof(struct token_perm_node), 0, SLAB_HWCACHE_ALIGN, NULL);
\tif (g_cache == NULL) {
\t\tpr_err("access_tokenid kmem_cache create failed\\n");
\t\treturn -ENOMEM;
\t}
\terr = misc_register(&access_tokenid_device);
\tif (err < 0) {
\t\tpr_err("access_tokenid register failed\\n");
\t\tkmem_cache_destroy(g_cache);
\t\tg_cache = NULL;
\t\treturn err;
\t}'''),
        ('''\tkmem_cache_destroy(g_cache);
\tmisc_deregister(&access_tokenid_device);''', '''\tstruct token_perm_node *node;

\t/* fops.owner prevents module exit while an open file is in use. */
\tmisc_deregister(&access_tokenid_device);
\twrite_lock(&token_rwlock);
\twhile (g_token_perm_root != NULL) {
\t\tnode = remove_node_by_token(&g_token_perm_root,
\t\t\t\t\t    g_token_perm_root->perm_data.token);
\t\tkmem_cache_free(g_cache, node);
\t}
\twrite_unlock(&token_rwlock);
\tkmem_cache_destroy(g_cache);
\tg_cache = NULL;'''),
    ]
    for old, new in changes:
        assert source.count(old) == 1, old
        source = source.replace(old, new, 1)
    return source
