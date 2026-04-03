"""
Service d'envoi d'emails avec Resend
Remplace les fonctions d'email mockées
"""
import os
import asyncio
import logging
import resend
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

# Configuration
resend.api_key = os.environ.get("RESEND_API_KEY", "")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "onboarding@resend.dev")
SENDER_NAME = os.environ.get("SENDER_NAME", "Édu-Connect MINEPST")

logger = logging.getLogger(__name__)


async def send_email_async(
    to_email: str,
    subject: str,
    html_content: str,
    from_name: Optional[str] = None
) -> dict:
    """
    Envoyer un email de manière asynchrone via Resend
    """
    if not resend.api_key or resend.api_key == "":
        logger.warning(f"RESEND_API_KEY not configured - Email to {to_email} NOT sent (mock mode)")
        print(f"""
        ========== EMAIL MOCK ==========
        To: {to_email}
        Subject: {subject}
        From: {from_name or SENDER_NAME} <{SENDER_EMAIL}>
        ================================
        {html_content[:200]}...
        ================================
        """)
        return {"status": "mocked", "message": "Email not sent (RESEND_API_KEY not configured)"}
    
    params = {
        "from": f"{from_name or SENDER_NAME} <{SENDER_EMAIL}>",
        "to": [to_email],
        "subject": subject,
        "html": html_content
    }
    
    try:
        # Run sync SDK in thread to keep FastAPI non-blocking
        email = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent successfully to {to_email}: {email.get('id')}")
        return {
            "status": "success",
            "email_id": email.get("id"),
            "recipient": to_email
        }
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "recipient": to_email
        }


def generate_email_html(
    titre: str,
    contenu: str,
    bouton_url: Optional[str] = None,
    bouton_texte: Optional[str] = None
) -> str:
    """
    Générer un template HTML d'email avec branding DRC
    """
    bouton_html = ""
    if bouton_url and bouton_texte:
        bouton_html = f"""
        <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 30px;">
            <tr>
                <td align="center">
                    <a href="{bouton_url}" style="background-color: #1E40AF; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                        {bouton_texte}
                    </a>
                </td>
            </tr>
        </table>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4;">
            <tr>
                <td align="center" style="padding: 40px 20px;">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%); padding: 30px; text-align: center; border-radius: 8px 8px 0 0;">
                                <h1 style="color: white; margin: 0; font-size: 24px;">
                                    🇨🇩 Édu-Connect MINEPST
                                </h1>
                                <p style="color: #E0E7FF; margin: 10px 0 0 0; font-size: 14px;">
                                    Ministère de l'Enseignement Primaire, Secondaire et Technique
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px 30px;">
                                <h2 style="color: #1F2937; margin: 0 0 20px 0; font-size: 20px;">
                                    {titre}
                                </h2>
                                <div style="color: #4B5563; line-height: 1.6; font-size: 15px;">
                                    {contenu}
                                </div>
                                {bouton_html}
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #F9FAFB; padding: 20px 30px; text-align: center; border-radius: 0 0 8px 8px; border-top: 1px solid #E5E7EB;">
                                <p style="color: #6B7280; font-size: 13px; margin: 0;">
                                    © 2026 MINEPST - République Démocratique du Congo<br>
                                    Système de Gestion Électronique de Documents
                                </p>
                                <p style="color: #9CA3AF; font-size: 12px; margin: 10px 0 0 0;">
                                    Ceci est un email automatique, merci de ne pas y répondre.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


# ============================================
# Fonctions d'email spécifiques à l'application
# ============================================

async def email_nouveau_document(
    destinataire_email: str,
    destinataire_nom: str,
    document_titre: str,
    document_ref: str,
    expediteur_nom: str,
    url_document: str
) -> dict:
    """Email : Nouveau document à traiter"""
    contenu = f"""
    <p>Bonjour <strong>{destinataire_nom}</strong>,</p>
    <p>Vous avez reçu un nouveau document à traiter de la part de <strong>{expediteur_nom}</strong> :</p>
    <table width="100%" cellpadding="10" cellspacing="0" style="background-color: #F3F4F6; border-radius: 5px; margin: 20px 0;">
        <tr>
            <td><strong>Titre :</strong></td>
            <td>{document_titre}</td>
        </tr>
        <tr>
            <td><strong>Référence :</strong></td>
            <td>{document_ref}</td>
        </tr>
    </table>
    <p>Veuillez consulter le document et prendre les mesures nécessaires.</p>
    """
    
    html = generate_email_html(
        titre="📄 Nouveau document à traiter",
        contenu=contenu,
        bouton_url=url_document,
        bouton_texte="Consulter le document"
    )
    
    return await send_email_async(
        to_email=destinataire_email,
        subject=f"Nouveau document : {document_titre}",
        html_content=html
    )


async def email_document_rejete(
    destinataire_email: str,
    destinataire_nom: str,
    document_titre: str,
    document_ref: str,
    raison_rejet: str,
    url_document: str
) -> dict:
    """Email : Document rejeté"""
    contenu = f"""
    <p>Bonjour <strong>{destinataire_nom}</strong>,</p>
    <p>Votre document a été rejeté :</p>
    <table width="100%" cellpadding="10" cellspacing="0" style="background-color: #FEF2F2; border-radius: 5px; margin: 20px 0; border-left: 4px solid #EF4444;">
        <tr>
            <td><strong>Titre :</strong></td>
            <td>{document_titre}</td>
        </tr>
        <tr>
            <td><strong>Référence :</strong></td>
            <td>{document_ref}</td>
        </tr>
        <tr>
            <td><strong>Raison :</strong></td>
            <td style="color: #DC2626;">{raison_rejet}</td>
        </tr>
    </table>
    <p>Veuillez apporter les corrections nécessaires et soumettre à nouveau.</p>
    """
    
    html = generate_email_html(
        titre="❌ Document rejeté",
        contenu=contenu,
        bouton_url=url_document,
        bouton_texte="Voir le document"
    )
    
    return await send_email_async(
        to_email=destinataire_email,
        subject=f"Document rejeté : {document_titre}",
        html_content=html
    )


async def email_document_valide(
    destinataire_email: str,
    destinataire_nom: str,
    document_titre: str,
    document_ref: str,
    url_document: str
) -> dict:
    """Email : Document validé"""
    contenu = f"""
    <p>Bonjour <strong>{destinataire_nom}</strong>,</p>
    <p>Bonne nouvelle ! Votre document a été validé avec succès :</p>
    <table width="100%" cellpadding="10" cellspacing="0" style="background-color: #F0FDF4; border-radius: 5px; margin: 20px 0; border-left: 4px solid #10B981;">
        <tr>
            <td><strong>Titre :</strong></td>
            <td>{document_titre}</td>
        </tr>
        <tr>
            <td><strong>Référence :</strong></td>
            <td>{document_ref}</td>
        </tr>
    </table>
    <p>Le document est maintenant finalisé et peut être consulté.</p>
    """
    
    html = generate_email_html(
        titre="✅ Document validé",
        contenu=contenu,
        bouton_url=url_document,
        bouton_texte="Consulter le document"
    )
    
    return await send_email_async(
        to_email=destinataire_email,
        subject=f"Document validé : {document_titre}",
        html_content=html
    )


async def email_transmission_externe(
    destinataire_email: str,
    document_titre: str,
    document_ref: str,
    expediteur_nom: str,
    message_perso: str,
    lien_telechargement: str,
    duree_validite_jours: int
) -> dict:
    """Email : Transmission externe avec lien temporaire"""
    message_html = f"<p>{message_perso}</p>" if message_perso else ""
    
    contenu = f"""
    <p>Bonjour,</p>
    <p><strong>{expediteur_nom}</strong> du MINEPST vous a transmis un document officiel :</p>
    <table width="100%" cellpadding="10" cellspacing="0" style="background-color: #FEF3C7; border-radius: 5px; margin: 20px 0; border-left: 4px solid #F59E0B;">
        <tr>
            <td><strong>Titre :</strong></td>
            <td>{document_titre}</td>
        </tr>
        <tr>
            <td><strong>Référence :</strong></td>
            <td>{document_ref}</td>
        </tr>
        <tr>
            <td><strong>Validité :</strong></td>
            <td>{duree_validite_jours} jours</td>
        </tr>
    </table>
    {message_html}
    <p style="color: #DC2626; font-weight: bold;">⚠️ Ce lien expire dans {duree_validite_jours} jours.</p>
    """
    
    html = generate_email_html(
        titre="📨 Document officiel transmis",
        contenu=contenu,
        bouton_url=lien_telechargement,
        bouton_texte="📥 Télécharger le Document"
    )
    
    subject = f"Document officiel MINEPST : {document_titre}"
    return await send_email_async(
        to_email=destinataire_email,
        subject=subject,
        html_content=html
    )


async def email_rappel_document(destinataire_email: str, destinataire_nom: str, document_titre: str, document_ref: str, url_document: str):
    """
    Envoyer un rappel email pour un document en attente de traitement
    
    Args:
        destinataire_email: Email du destinataire
        destinataire_nom: Nom complet du destinataire
        document_titre: Titre du document
        document_ref: Numéro de référence du document
        url_document: URL pour accéder au document
    
    Returns:
        dict: Résultat de l'envoi
    """
    try:
        subject = f"⏰ Rappel: Document en attente - {document_ref}"
        
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">⏰ Rappel Document</h1>
            </div>
            
            <div style="padding: 30px; background-color: #f7fafc;">
                <p style="font-size: 16px; color: #2d3748;">Bonjour <strong>{destinataire_nom}</strong>,</p>
                
                <p style="font-size: 14px; color: #4a5568; line-height: 1.6;">
                    Nous vous rappelons qu'un document est en attente de votre traitement :
                </p>
                
                <div style="background-color: white; border-left: 4px solid #f59e0b; padding: 20px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>📄 Titre:</strong> {document_titre}</p>
                    <p style="margin: 5px 0;"><strong>🔖 Référence:</strong> {document_ref}</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{url_document}" 
                       style="background-color: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                        📂 Accéder au Document
                    </a>
                </div>
                
                <p style="font-size: 12px; color: #718096; margin-top: 30px;">
                    Ce rappel est envoyé automatiquement par le système Édu-Connect.
                </p>
            </div>
        </div>
        """
        
        return await send_email_async(
            to_email=destinataire_email,
            subject=subject,
            html_content=html_body
        )
    
    except Exception as e:
        print(f"Erreur envoi email rappel: {e}")
        return {"status": "error", "error": str(e)}



async def email_rapport_trimestriel(destinataire_email: str, destinataire_nom: str, periode: str, url_rapport: str):
    """
    Envoyer un email avec le rapport trimestriel
    
    Args:
        destinataire_email: Email du destinataire
        destinataire_nom: Nom complet du destinataire
        periode: Période du rapport (ex: "Q1 2026")
        url_rapport: URL pour télécharger le rapport
    
    Returns:
        dict: Résultat de l'envoi
    """
    try:
        subject = f"📊 Rapport Trimestriel {periode} - Édu-Connect"
        
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">📊 Rapport Trimestriel</h1>
            </div>
            
            <div style="padding: 30px; background-color: #f7fafc;">
                <p style="font-size: 16px; color: #2d3748;">Bonjour <strong>{destinataire_nom}</strong>,</p>
                
                <p style="font-size: 14px; color: #4a5568; line-height: 1.6;">
                    Le rapport trimestriel <strong>{periode}</strong> est maintenant disponible.
                </p>
                
                <div style="background-color: white; border-left: 4px solid #10b981; padding: 20px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>📅 Période:</strong> {periode}</p>
                    <p style="margin: 5px 0;"><strong>📈 Type:</strong> Rapport d'activité GED</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{url_rapport}" 
                       style="background-color: #10b981; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                        📥 Télécharger le Rapport
                    </a>
                </div>
                
                <p style="font-size: 12px; color: #718096; margin-top: 30px;">
                    Ce rapport est généré automatiquement par le système Édu-Connect.
                </p>
            </div>
        </div>
        """
        
        return await send_email_async(
            to_email=destinataire_email,
            subject=subject,
            html_content=html_body
        )
    
    except Exception as e:
        print(f"Erreur envoi email rapport: {e}")
        return {"status": "error", "error": str(e)}
    
    except Exception as e:
        print(f"Erreur envoi email rapport: {e}")
        return False
