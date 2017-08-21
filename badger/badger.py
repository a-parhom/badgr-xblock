"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
import logging
from django.conf import settings
from xblock.core import XBlock
from django.contrib.auth.models import User
from xblock.fields import Scope, Integer, String, Float, List, Boolean, ScopeIds
from xblockutils.resources import ResourceLoader
from xblock.fragment import Fragment
from xblockutils.studio_editable import StudioEditableXBlockMixin
from xblockutils.settings import XBlockWithSettingsMixin
logger = logging.getLogger(__name__)
loader = ResourceLoader(__name__)

@XBlock.wants('badging')
@XBlock.wants('user')
class BadgerXBlock(StudioEditableXBlockMixin, XBlockWithSettingsMixin, XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    # TO-DO: delete count, and define your own fields.
    display_name = String(
        display_name="Display Name",
        help="This name appears in the horizontal navigation at the top of the page.",
        scope=Scope.settings,
        default="Badger"
    )

    badge_class_name = String(
        display_name="Badge Class",
        help="This is the name of the specific badge class used in this graded subsection.",
        scope=Scope.settings,
        default="NewBadgeClass"
    )

    badge_slug = String(
        display_name="Badge slug",
        help="must be lower case unique name.",
        scope=Scope.settings,
        default="test-badge"
    )

    image_url = String(
        display_name="Image url",
        help="The url for the badge image located in static files",
        scope=Scope.settings,
        default="/static/my-badge"
    )

    criteria = String(
        display_name="Criteria",
        help="How does one earn this badge?",
        scope=Scope.settings,
        default="Visit a page with an award block."
    )

    description = String(
        display_name="Description",
        help="What is this badge",
        scope=Scope.settings,
        default="A Shiny badge, given to anyone who finds it!"
    )

    section_title = String(
        display_name="Section title",
        help="See the display name of this section",
        scope=Scope.settings,
        default="Section"
    )

    single_activity = Boolean(
        display_name='Single activity',
        default=False,
        scope=Scope.settings,
        help='Is this badge for a single activity or an entire section?'
    )

    activity_title = String(
        display_name='Activity title.',
        help='Give the title of the activity in this section for the award.',
        scope=Scope.settings,
    )
    pass_mark = Float(
        display_name='Pass mark',
        default=80.0, 
        scope=Scope.settings,
        help="Minium grade required to award this badge",
    )

    count = Integer(
        default=0, 
        scope=Scope.user_state,
        help="A simple counter, to show something happening",
    )

    award_message = String(
        display_name='Award message',
        default='Well done you are an all star!',
        scope=Scope.settings,
        help='Message the user will see upon receiving a badge',
    )

    motivation_message = String(
        display_name='Motivational message',
        default = 'Keep trying and learning, never give up.',
        scope=Scope.settings,
        help='Message the user will see if they do not quailify for a badge'
    )

    editable_fields = ('display_name', 'badge_class_name', 'badge_slug', 'image_url', 'criteria', 'description', 'pass_mark', 'section_title', 'award_message', 'motivation_message', 'single_activity', 'activity_title',)
    show_in_read_only_mode = True
 
    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.

    def award_badge(self, badge_service):
        user_service = self.runtime.service(self, 'user')
        badge_class = badge_service.get_badge_class(
            slug='general_award', issuing_component='my_org__award_block',
            description="A Shiny badge, given to anyone who finds it!",
            criteria="Visit a page with an award block.",
            display_name='lid',
            # This attribute not available in all runtimes,
            # but if we have both of these services, it's a safe bet we're in the LMS.
            course_id=self.runtime.course_id,
            # The path to this file should be somewhere relative to your XBlock's package.
            # It should be a square PNG file less than 250KB in size.
            image_file_handle=pkg_resources.resource_stream(__name__, 'badges_images/coffee.png'),
            create=True
            # Badge image should be a square PNG file less than 250KB in size.
        )
        # Award the badge.
        #if not badge_class.get_for_user(self.runtime.get_real_user(self.runtime.anonymous_student_id)):
        badge_class.award(self.runtime.get_real_user(self.runtime.anonymous_student_id))

    def new_award_badge(self, badge_service):
        
        badge_class = badge_service.get_badge_class(
            slug=self.badge_slug, issuing_component='my_org__award_block',
            description=self.description,
            criteria=self.criteria,
            display_name=self.badge_class_name,
            course_id=self.runtime.course_id,
            image_file_handle='http://0.0.0.0:8000/asset-v1:edX+DemoX+Demo_Course+type@asset+block@lid_test.png',
            create=True
        )
        # /asset-v1:edX+DemoX+Demo_Course+type@asset+block@lid_test.png
        # Award the badge.
        #if not badge_class.get_for_user(self.runtime.get_real_user(self.runtime.anonymous_student_id)):
        user = self.runtime.get_real_user(self.runtime.anonymous_student_id)
        badge_class.award(user)

    def student_view(self, context=None):
        """
        The primary view of the BadgerXBlock, shown to students
        when viewing courses.
        """
        badge_service = self.runtime.service(self, 'badging')
        user_service = self.runtime.service(self, 'user')
        html = self.resource_string("static/html/badger.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/badger.css"))
        frag.add_javascript(self.resource_string("static/js/src/badger.js"))
        frag.initialize_js('BadgerXBlock', {
            'user': user.username,
            'pass_mark': self.pass_mark,
            'section_title': self.section_title,
            'award_message': self.award_message,
            'motivation_message': self.motivation_message
        })
        
        if user_service and badge_service:
            self.new_award_badge(badge_service)
        return frag


    def studio_view(self, context):
        """
        Render a form for editing this XBlock
        """
        frag = Fragment()
        context = {'fields': []}
        # Build a list of all the fields that can be edited:
        for field_name in self.editable_fields:
            field = self.fields[field_name]
            assert field.scope in (Scope.content, Scope.settings), (
                "Only Scope.content or Scope.settings fields can be used with "
                "StudioEditableXBlockMixin. Other scopes are for user-specific data and are "
                "not generally created/configured by content authors in Studio."
            )
            field_info = self._make_field_info(field_name, field)
            if field_info is not None:
                context["fields"].append(field_info)
        frag.content = loader.render_django_template("static/html/badger_edit.html", context)
        frag.add_javascript(loader.load_unicode("static/js/src/badger_edit.js"))
        frag.initialize_js('StudioEditableXBlockMixin')
        return frag


    # TO-DO: change this handler to perform your own actions.  You may need more
    # than one handler, or you may not need any handlers at all.
    @XBlock.json_handler
    def increment_count(self, data, suffix=''):
        """
        An example handler, which increments the data.
        """
        # Just to show data coming in...
        assert data['hello'] == 'world'

        self.count += 1
        return {"count": self.count}

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("BadgerXBlock",
             """<badger/>
             """),
            ("Multiple BadgerXBlock",
             """<vertical_demo>
                <badger/>
                <badger/>
                <badger/>
                </vertical_demo>
             """),
        ]
