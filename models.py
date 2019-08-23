# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from anthill.framework.utils import timezone
from anthill.framework.utils.asynchronous import as_future
from anthill.platform.api.internal import InternalAPIMixin


class Backup(db.Model):
    __tablename__ = 'backups'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(512))
    file = db.Column(db.FileType(upload_to='backups'), nullable=False)
    author_id = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, default=timezone.now)

    recoveries = db.relationship('Recovery', backref='backup', lazy='dynamic')

    def __repr__(self):
        return '<Backup(name=%s)>' % self.name

    @as_future
    def recover(self):
        pass


class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(512), nullable=False)

    recoveries = db.relationship('Recovery', backref='group', lazy='dynamic')
    backups = db.relationship('Backup', backref='group', lazy='dynamic')

    def __repr__(self):
        return '<Group(name=%s)>' % self.name


class Recovery(InternalAPIMixin, db.Model):
    __tablename__ = 'recoveries'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    backup_id = db.Column(db.Integer, db.ForeignKey('backups.id'))
    author_id = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, default=timezone.now)

    @property
    def item(self):
        return self.backup or self.group

    def __repr__(self):
        return repr(self.item)

    async def get_author(self):
        return await self.internal_request('login', 'get_user', user_id=self.author_id)

