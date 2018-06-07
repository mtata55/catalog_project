from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


category1 = Category(name = "Soccer")
session.add(category1)
session.commit()

item1 = Item(name = "Soccer Ball", description = "Original Nike Soccer Ball.", category = category1, creator='mtata@gmail.com')
session.add(item1)
session.commit()


category2 = Category(name = "Basketball")
session.add(category2)
session.commit()

item2 = Item(name = "Basketball", description = "Original Nike Basketball.", category = category2, creator='mtata@gmail.com')
session.add(item2)
session.commit()

category3 = Category(name = "Baseball")
session.add(category3)
session.commit()


category4 = Category(name = "Frisbee")
session.add(category4)
session.commit()


category5 = Category(name = "Snowboarding")
session.add(category5)
session.commit()

print "added dummy data!"
