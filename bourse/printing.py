from django.conf import settings
from .models import Event, UserList, Item, Order, OrderItem
from math import ceil
# ReportLab
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, BaseDocTemplate, Paragraph, Table, TableStyle, Frame, PageTemplate, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        # Change the position of this to wherever you want the page number to be
        self.drawRightString(11*cm, .5*cm, "Page %d de %d" % (self._pageNumber, page_count))

class MyPrint:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4   
        elif pagesize == 'TruncA4':
            self.pagesize = (18*cm,29.7*cm)
        self.width, self.height = self.pagesize
        self.c = canvas.Canvas(buffer,pagesize=self.pagesize)
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle('WhiteHeading1',parent=self.styles['Heading1'],textColor=colors.white))
        self.styles.add(ParagraphStyle('WhiteHeading2',parent=self.styles['Heading2'],textColor=colors.white))
        self.styles.add(ParagraphStyle('WhiteBodyText',parent=self.styles['BodyText'],textColor=colors.white))
    
    # helper for positionning
    def coord(self, x, y, unit=1):
        x, y = x * unit, self.height -  y * unit
        return x, y

    # Création du document PDF liste / étiquettes. C'est bourrin, il y a sans doute moyen d'optimiser...
    def createDoc(self,event,user_list,user_list_items,post=False):
        buffer=self.buffer
        self.c.setTitle('Fiche Inscription Bourse Woopy')
        event_desc = event.event_name + ' du ' + event.date_only()
        user_full_name_desc = 'Vendeur n°' + str(user_list.user.id) + ' - ' + user_list.user.first_name + ' ' + user_list.user.last_name
        if post:
            my_black = colors.white
            my_grey = colors.white
            my_heading1 = self.styles['WhiteHeading1']
            my_heading2 = self.styles['WhiteHeading2']
            my_bodytext = self.styles['WhiteBodyText']
        else:
            my_black = colors.black
            my_grey = colors.lightgrey
            my_heading1 = self.styles['Heading1']
            my_heading2 = self.styles['Heading2']
            my_bodytext = self.styles['BodyText']

        title = Paragraph(event_desc, my_heading1)
        seller = Paragraph(user_full_name_desc, my_heading2)

        table_data = []
        price_tags_data = []

        nb_sold = 0
        total_seller = 0
        nbMaxLinesPerPage = 18 # /!\ Pas plus de 18 éléments par page.
        page_cur=1
        # On parcourt les éléments du vendeur pour générer les pages du pdf
        for i, item in enumerate(user_list_items): 
            # On est sur une nouvelle page, affichage titre - vendeur, initialisation tableaux
            if i%nbMaxLinesPerPage == 0: 
                # Titre et Vendeur
                title.wrapOn(self.c, 17*cm, 1*cm)
                title.drawOn(self.c, *self.coord(2,2,cm))
                seller.wrapOn(self.c, 17*cm, 1*cm)
                seller.drawOn(self.c, *self.coord(2,3,cm))
                # Vertical line
                if not post:
                    self.c.setLineWidth(0.5)
                    self.c.line(18*cm,0,18*cm,self.height)
                # Init Tabs
                table_data = []
                price_tags_data = []
                table_data.append(['id','Description','Prix de vente','Vendu','Net Vendeur'])
            # Variables pour chaque ligne
            id_full_item = str(event.id) + '-' + str(user_list.user.id) + '-' + str(item.pk) # event id - user id - item id
            price_currency = str(item.price) + ' ' + settings.CURRENCY
            item_name_p = Paragraph(item.name,my_bodytext)
            if len(item.name) > 25:
                item_name_trunc = item.name[0:24] + '...'
            else: 
                item_name_trunc = item.name
            if item.is_sold:
                is_sold_render = 'X'
                nb_sold = nb_sold + 1
                net_price = str(item.price - settings.COMMISSION) + ' ' + settings.CURRENCY
                total_seller = total_seller + item.price - settings.COMMISSION
            else:
                is_sold_render = ' '
                net_price = ' '
            # Ajout au tableau
            table_data.append([item.pk,item_name_p,price_currency,is_sold_render,net_price])
            # Ajout aux étiquettes
            price_tags_data.append([id_full_item])
            price_tags_data.append([item_name_trunc])
            price_tags_data.append([price_currency])
            # Si dernière ligne du tableau ou nbMaxLinesPerPage lignes affichées
            if ( i == len(user_list_items) - 1 ) or i%nbMaxLinesPerPage == nbMaxLinesPerPage-1: 
                # Si dernière ligne affichage de l'encadré à signer
                if ( i == len(user_list_items) - 1 ):
                    tot_label = 'Total :'
                    table_fin = Table([
                                            [Paragraph('Pièce d’identité vérifiée : oui-non -  Règlement signé : oui-non',my_bodytext)],
                                            [Paragraph('<b>Date et Signature:</b>',my_bodytext)],
                                            [Paragraph('<b>Cadre réservé à la restitution (jeux/argent) :</b><br/>Je déclare exacte la restitution de mes jeux invendus et/ou le paiement de mes ventes.<br/><b>Date et Signature:</b>',my_bodytext)]
                                         ],
                                         colWidths=11.5*cm,rowHeights=[1*cm,1.5*cm,3.5*cm])
                    table_fin.setStyle(TableStyle([('BOX',(0,2),(-1,-1),0.5,my_black),('VALIGN',(0,0),(-1,-1),'TOP')]))
                    table_fin.wrapOn(self.c,11.5*cm,3.5*cm)
                    table_fin.drawOn(self.c,2*cm,2*cm)
                else:
                    tot_label = 'Sous-total :'
                if nb_sold == 0:
                    sum_sold = ' '
                    sum_net = ' '
                else:
                    sum_sold = str(nb_sold)
                    sum_net = str(total_seller) + ' ' + settings.CURRENCY
                # Ajout du total au tableau
                table_data.append(['','',tot_label,sum_sold,sum_net])
                # Create the item table
                item_table = Table(table_data, colWidths=[2*cm,5*cm,2.5*cm,1.5*cm,2.5*cm])
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -2), 0.25, my_black),
                                                ('BOX', (0, 0), (-1, -2), 0.25, my_black),
                                                ('ALIGN',(0, 1),(-1, -1),'RIGHT'),
                                                ('ALIGN',(3, 1),(-2, -1),'CENTER'),
                                                ('GRID', (-2, -1), (-1, -1), 0.25, my_black)
                                                ]))
                # Passage en blanc de toutes les données du tableau, sauf les 'X' et totaux.
                if post:
                    item_table.setStyle(TableStyle([('TEXTCOLOR', (0, 0), (-3, -1), my_black),('TEXTCOLOR', (-1, 0), (-1, -2), my_black),('TEXTCOLOR', (-3, 0), (-2, 1), my_black)]))
                # Affichage du tableau
                item_table.wrapOn(self.c, 15*cm, 18*cm)
                item_table.drawOn(self.c, *self.coord(2,5+0.6*len(table_data),cm))
                # Create the price tags table
                if not post:
                    price_tags_table = Table(price_tags_data,colWidths=[3*cm])
                    rowNumb = len(price_tags_data)
                    for r in range(0, rowNumb):
                        if r%3 == 0:
                            price_tags_table.setStyle(TableStyle([('BOX',(0,r),(-1,r+2),0.5,my_black),
                                                                ('TOPPADDING',(0,r),(-1,r),0),
                                                                ('BOTTOMPADDING',(0,r),(-1,r),-0)]))
                        elif r%3 == 1:
                            price_tags_table.setStyle(TableStyle([('LINEABOVE',(0,r),(-1,r),0.5,my_grey),
                                                                ('ALIGN',(0,r),(-1,r),'CENTER'),
                                                                ('TOPPADDING',(0,r),(-1,r),0),
                                                                ('BOTTOMPADDING',(0,r),(-1,r),-3),
                                                                ('FONTSIZE',(0,r),(-1,r),6)]))
                        else:
                            price_tags_table.setStyle(TableStyle([('LINEABOVE',(0,r),(-1,r),0.5,my_grey),
                                                                ('FONTSIZE',(0,r),(-1,r),18),
                                                                ('TOPPADDING',(0,r),(-1,r),0),
                                                                ('BOTTOMPADDING',(0,r),(-1,r),10),
                                                                ('ALIGN',(0,r),(-1,r),'RIGHT'),
                                                                ('VALIGN',(0,r),(-1,r),'MIDDLE')]))
                    price_tags_table.wrapOn(self.c, 3*cm, 3*cm)
                    price_tags_table.drawOn(self.c, *self.coord(18,28,cm))
                # Pages
                pages_label = Paragraph('page ' + str(page_cur) + ' sur ' + str(ceil(len(user_list_items)/nbMaxLinesPerPage)),my_bodytext)
                pages_label.wrapOn(self.c,5*cm,1*cm)
                pages_label.drawOn(self.c,9.5*cm,0.5*cm)
                page_cur += 1
                # Page break
                if i%nbMaxLinesPerPage == nbMaxLinesPerPage-1:
                    self.c.showPage()
        # Sauvegarde et retour du fichier
        self.c.save()
        pdf = buffer.getvalue()
        buffer.close()
        return pdf
    
    # Création du document PDF facture
    def createInvoice(self,event,order,order_items,form_data):
        buffer=self.buffer
        self.c.setTitle('Facture de vente n°' + str(order.id))
        event_desc = event.event_name + ' du ' + event.date_only()
        my_black = colors.black
        my_grey = colors.lightgrey
        # Titre de page
        title = Paragraph(event_desc, self.styles['Heading1'])
        # Sous-titre
        sub_title = Paragraph('Facture de vente n°' + str(order.id), self.styles['Heading2'])
        # Box vendeur
        seller_address = [[settings.ASSO_NAME]]
        for line in settings.ASSO_ADDR:
            seller_address.append([line])
        seller_address_table = Table(seller_address)
        seller_address_table.setStyle(TableStyle([('BOX',(0,0),(-1,-1),0.5,my_grey)]))
        # Box acheteur ( A PEAUFINER )
        client_address = [[Paragraph('Client Facturé :',self.styles['BodyText'])],
                            [form_data['client_name']],[form_data['addr_1']],[form_data['addr_2']],[form_data['cp_city']]
                        ]
        client_address_table = Table(client_address)
        client_address_table.setStyle(TableStyle([('BOX',(0,1),(-1,-1),0.5,my_grey)]))

        total_invoice = 0
        nbMaxLinesPerPage = 18 # /!\ Pas plus de 18 éléments par page.
        page_cur=1
        # On parcourt les éléments de la vente pour générer les pages du pdf
        table_data = []
        for i,element in enumerate(order_items):

            # On est sur une nouvelle page, affichage titre sous-titre - coordo asso et acheteur, initialisation tableaux
            if i%nbMaxLinesPerPage == 0: 
                # Titre et Sous-Titre
                title.wrapOn(self.c, 17*cm, 1*cm)
                title.drawOn(self.c, *self.coord(2,2,cm))
                sub_title.wrapOn(self.c, 17*cm, 1*cm)
                sub_title.drawOn(self.c, *self.coord(2,3,cm))
                # Box vendeur
                seller_address_table.wrapOn(self.c,5*cm,4*cm)
                seller_address_table.drawOn(self.c, *self.coord(2,6,cm))
                # Box acheteur
                client_address_table.wrapOn(self.c,5*cm,4*cm)
                client_address_table.drawOn(self.c, *self.coord(10,6,cm))
                # Init Tabs
                table_data = []
                table_data.append(['Description','Prix de vente'])
            
            # Variables pour chaque ligne
            total_invoice = total_invoice + element.item.price

            # Ajout au tableau
            table_data.append([element.item.name,str(element.item.price) + ' ' + settings.CURRENCY ])

            # Si dernière ligne du tableau ou nbMaxLinesPerPage lignes affichées
            if ( i == len(order_items) - 1 ) or i%nbMaxLinesPerPage == nbMaxLinesPerPage-1: 
                if ( i == len(order_items) - 1 ):
                    tot_label = 'Total :'
                else:
                    tot_label = 'Sous-total :'
                # Ajout du total au tableau
                sum_net = str(total_invoice) + ' ' + settings.CURRENCY
                table_data.append([tot_label,sum_net])
                # Create the item table
                item_table = Table(table_data, colWidths=[12*cm,3*cm])
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -2), 0.25, my_black),
                                                ('BOX', (0, 0), (-1, -2), 0.25, my_black),
                                                ('ALIGN',(1, 1),(-1, -1),'RIGHT'),
                                                ('ALIGN',(1, 0),(-1, 0),'CENTER'),
                                                ('ALIGN',(0, -1),(1, -1),'RIGHT'),
                                                ('GRID', (1, -1), (-1, -1), 0.25, my_black)
                                                ]))
                item_table.wrapOn(self.c, 15*cm, 18*cm)
                item_table.drawOn(self.c, *self.coord(2,8+0.6*len(table_data),cm))
                # Pages
                pages_label = Paragraph('page ' + str(page_cur) + ' sur ' + str(ceil(len(order_items)/nbMaxLinesPerPage)),self.styles['BodyText'])
                pages_label.wrapOn(self.c,5*cm,1*cm)
                pages_label.drawOn(self.c,9.5*cm,0.5*cm)
                page_cur += 1
                # Page break
                if i%nbMaxLinesPerPage == nbMaxLinesPerPage-1:
                    self.c.showPage()
        
        # Sauvegarde et retour du fichier
        self.c.save()
        pdf = buffer.getvalue()
        buffer.close()
        return pdf