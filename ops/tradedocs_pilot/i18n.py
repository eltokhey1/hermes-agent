"""TradeDocs UI translations: Arabic, English, French and Spanish."""
LANGUAGES = ("ar", "en", "fr", "es")
MESSAGES = {
 "app_title": {"ar": "تدقيق مستندات التجارة الدولية", "en": "International Trade Document Review", "fr": "Contrôle des documents du commerce international", "es": "Revisión de documentos de comercio internacional"},
 "lc_number": {"ar": "رقم الاعتماد", "en": "Letter of credit number", "fr": "Numéro du crédit documentaire", "es": "Número de crédito documentario"},
 "origin_country": {"ar": "بلد المنشأ", "en": "Country of origin", "fr": "Pays d'origine", "es": "País de origen"},
 "import_country": {"ar": "بلد الاستيراد", "en": "Import country", "fr": "Pays d'importation", "es": "País de importación"},
 "export_country": {"ar": "بلد التصدير", "en": "Export country", "fr": "Pays d'exportation", "es": "País de exportación"},
 "shipment": {"ar": "الشحنة", "en": "Shipment", "fr": "Expédition", "es": "Envío"},
 "remaining_quantity": {"ar": "الكمية المتبقية", "en": "Remaining quantity", "fr": "Quantité restante", "es": "Cantidad restante"},
 "remaining_amount": {"ar": "القيمة المتبقية", "en": "Remaining amount", "fr": "Montant restant", "es": "Importe restante"},
 "needs_review": {"ar": "يحتاج إلى مراجعة", "en": "Needs review", "fr": "À vérifier", "es": "Requiere revisión"},
 "unknown_regulation": {"ar": "المتطلبات المحلية غير موثقة بعد", "en": "Local requirements not yet verified", "fr": "Exigences locales non encore vérifiées", "es": "Requisitos locales aún no verificados"},
 "dhl_tracking": {"ar": "رقم تتبع DHL", "en": "DHL tracking number", "fr": "Numéro de suivi DHL", "es": "Número de seguimiento DHL"},
 "signature": {"ar": "التوقيع", "en": "Signature", "fr": "Signature", "es": "Firma"},
 "stamp": {"ar": "الختم", "en": "Stamp", "fr": "Cachet", "es": "Sello"},
 "payment_due": {"ar": "تاريخ استحقاق الدفع", "en": "Payment due date", "fr": "Date d'échéance du paiement", "es": "Fecha de vencimiento del pago"},
}
def translate(key, language="en"):
    if language not in LANGUAGES:
        raise ValueError("Unsupported language")
    return MESSAGES[key][language]

def check_catalog():
    if any(set(translations) != set(LANGUAGES) or not all(translations.values()) for translations in MESSAGES.values()):
        raise ValueError("Incomplete translation catalog")
    return True
