import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Remove legacy stock_analytic views that reference analytic_account_id.
    These were valid in v15 but the field no longer exists in v19.
    Removing them here (before data load) prevents validation errors in modules
    that load before stock_analytic finishes its upgrade (e.g. stock_ux).
    """
    if not version:
        return
    cr.execute("""
        DELETE FROM ir_ui_view
        WHERE id IN (
            SELECT imd.res_id
            FROM ir_model_data imd
            WHERE imd.model = 'ir.ui.view'
              AND imd.module = 'stock_analytic'
        )
        AND arch_db::text LIKE '%analytic_account_id%'
    """)
    deleted = cr.rowcount
    if deleted:
        _logger.info(
            "stock_analytic pre-migrate: removed %d legacy view(s) with "
            "analytic_account_id (replaced by analytic_distribution in v19)",
            deleted,
        )
