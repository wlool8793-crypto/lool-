import React from 'react';
import { CVData } from '@/types';
import { CalendarDays, MapPin, Mail, Phone, Globe, Github, Linkedin, Twitter, ExternalLink } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CreativeTemplateProps {
  data: CVData;
  className?: string;
}

const CreativeTemplate: React.FC<CreativeTemplateProps> = ({ data, className }) => {
  const { personalInfo, professionalSummary, workExperience, education, skills, projects, certifications, languages } = data;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short'
    });
  };

  const getSkillLevelColor = (level: string) => {
    switch (level) {
      case 'expert': return 'bg-marriage-600';
      case 'advanced': return 'bg-primary-600';
      case 'intermediate': return 'bg-accent-600';
      case 'beginner': return 'bg-secondary-400';
      default: return 'bg-secondary-300';
    }
  };

  return (
    <div className={cn(
      'w-full max-w-4xl mx-auto bg-white shadow-2xl print:shadow-none',
      'overflow-hidden border-8 border-primary-600',
      className
    )}>
      {/* Creative Header with Diagonal Design */}
      <div className="relative bg-gradient-to-br from-primary-600 via-primary-700 to-marriage-600 text-white">
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="relative z-10 p-8 pb-16">
          <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
            {personalInfo.profileImage && (
              <div className="flex-shrink-0">
                <img
                  src={personalInfo.profileImage}
                  alt={personalInfo.fullName}
                  className="w-32 h-32 rounded-full border-4 border-white shadow-lg object-cover"
                />
              </div>
            )}
            <div className="flex-1 text-center md:text-left">
              <h1 className="text-4xl font-bold mb-2 tracking-tight">{personalInfo.fullName}</h1>
              {personalInfo.headline && (
                <p className="text-xl text-primary-100 mb-4">{personalInfo.headline}</p>
              )}
              <div className="flex flex-wrap justify-center md:justify-start gap-3 text-sm">
                {personalInfo.email && (
                  <div className="flex items-center gap-1 bg-white/20 px-3 py-1 rounded-full">
                    <Mail className="w-4 h-4" />
                    <span>{personalInfo.email}</span>
                  </div>
                )}
                {personalInfo.phone && (
                  <div className="flex items-center gap-1 bg-white/20 px-3 py-1 rounded-full">
                    <Phone className="w-4 h-4" />
                    <span>{personalInfo.phone}</span>
                  </div>
                )}
                {personalInfo.address && (
                  <div className="flex items-center gap-1 bg-white/20 px-3 py-1 rounded-full">
                    <MapPin className="w-4 h-4" />
                    <span>{personalInfo.address}</span>
                  </div>
                )}
              </div>
              <div className="flex flex-wrap justify-center md:justify-start gap-3 mt-3">
                {personalInfo.linkedin && (
                  <a href={personalInfo.linkedin} className="text-white hover:text-primary-200 transition-colors">
                    <Linkedin className="w-5 h-5" />
                  </a>
                )}
                {personalInfo.github && (
                  <a href={personalInfo.github} className="text-white hover:text-primary-200 transition-colors">
                    <Github className="w-5 h-5" />
                  </a>
                )}
                {personalInfo.website && (
                  <a href={personalInfo.website} className="text-white hover:text-primary-200 transition-colors">
                    <Globe className="w-5 h-5" />
                  </a>
                )}
                {personalInfo.twitter && (
                  <a href={personalInfo.twitter} className="text-white hover:text-primary-200 transition-colors">
                    <Twitter className="w-5 h-5" />
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Diagonal Bottom */}
        <div className="absolute bottom-0 left-0 right-0 h-8 bg-white clip-path-diagonal"></div>
      </div>

      <div className="p-8">
        {/* Summary Section */}
        {professionalSummary && (
          <section className="mb-8">
            <h2 className="text-2xl font-bold text-primary-700 mb-4 pb-2 border-b-2 border-primary-200">
              Professional Summary
            </h2>
            <p className="text-gray-700 leading-relaxed">{professionalSummary}</p>
          </section>
        )}

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-8">
            {/* Experience Section */}
            {workExperience.length > 0 && (
              <section>
                <h2 className="text-2xl font-bold text-primary-700 mb-4 pb-2 border-b-2 border-primary-200">
                  Experience
                </h2>
                <div className="space-y-6">
                  {workExperience.map((exp) => (
                    <div key={exp.id} className="relative pl-6 border-l-2 border-primary-200">
                      <div className="absolute -left-2 top-0 w-4 h-4 bg-primary-600 rounded-full"></div>
                      <div className="bg-gray-50 p-4 rounded-lg hover:shadow-md transition-shadow">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900">{exp.position}</h3>
                            <p className="text-primary-600 font-medium">{exp.company}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm text-gray-600 flex items-center gap-1">
                              <CalendarDays className="w-4 h-4" />
                              {formatDate(exp.startDate)} - {exp.current ? 'Present' : formatDate(exp.endDate)}
                            </p>
                            <p className="text-sm text-gray-500 flex items-center gap-1">
                              <MapPin className="w-4 h-4" />
                              {exp.location}
                            </p>
                          </div>
                        </div>
                        <p className="text-gray-700 mb-3">{exp.description}</p>
                        {exp.achievements.length > 0 && (
                          <ul className="list-disc list-inside text-gray-600 space-y-1">
                            {exp.achievements.map((achievement, index) => (
                              <li key={index} className="text-sm">{achievement}</li>
                            ))}
                          </ul>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Projects Section */}
            {projects.length > 0 && (
              <section>
                <h2 className="text-2xl font-bold text-primary-700 mb-4 pb-2 border-b-2 border-primary-200">
                  Projects
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {projects.map((project) => (
                    <div key={project.id} className="bg-gray-50 p-4 rounded-lg hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">{project.title}</h3>
                        {project.url && (
                          <a href={project.url} className="text-primary-600 hover:text-primary-800">
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mb-3">{project.description}</p>
                      <div className="flex flex-wrap gap-2 mb-2">
                        {project.technologies.map((tech, index) => (
                          <span key={index} className="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded">
                            {tech}
                          </span>
                        ))}
                      </div>
                      <p className="text-xs text-gray-500">
                        <CalendarDays className="w-3 h-3 inline mr-1" />
                        {formatDate(project.startDate)} - {project.endDate ? formatDate(project.endDate) : 'Ongoing'}
                      </p>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>

          {/* Right Column */}
          <div className="space-y-8">
            {/* Skills Section */}
            {skills.length > 0 && (
              <section>
                <h2 className="text-xl font-bold text-primary-700 mb-4 pb-2 border-b-2 border-primary-200">
                  Skills
                </h2>
                <div className="space-y-4">
                  {['technical', 'soft', 'tool', 'framework'].map((category) => {
                    const categorySkills = skills.filter(skill => skill.category === category);
                    if (categorySkills.length === 0) return null;

                    return (
                      <div key={category}>
                        <h3 className="font-semibold text-gray-800 mb-2 capitalize">{category}</h3>
                        <div className="space-y-2">
                          {categorySkills.map((skill) => (
                            <div key={skill.id}>
                              <div className="flex justify-between items-center mb-1">
                                <span className="text-sm text-gray-700">{skill.name}</span>
                                <span className="text-xs text-gray-500 capitalize">{skill.level}</span>
                              </div>
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div
                                  className={cn('h-2 rounded-full transition-all duration-300', getSkillLevelColor(skill.level))}
                                  style={{
                                    width: skill.level === 'expert' ? '100%' :
                                           skill.level === 'advanced' ? '80%' :
                                           skill.level === 'intermediate' ? '60%' : '40%'
                                  }}
                                ></div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </section>
            )}

            {/* Education Section */}
            {education.length > 0 && (
              <section>
                <h2 className="text-xl font-bold text-primary-700 mb-4 pb-2 border-b-2 border-primary-200">
                  Education
                </h2>
                <div className="space-y-4">
                  {education.map((edu) => (
                    <div key={edu.id} className="bg-gray-50 p-3 rounded-lg">
                      <h3 className="font-semibold text-gray-900">{edu.degree}</h3>
                      <p className="text-primary-600 text-sm">{edu.field}</p>
                      <p className="text-gray-600 text-sm">{edu.institution}</p>
                      <div className="flex justify-between items-center mt-2">
                        <p className="text-xs text-gray-500">
                          <CalendarDays className="w-3 h-3 inline mr-1" />
                          {formatDate(edu.startDate)} - {formatDate(edu.endDate)}
                        </p>
                        {edu.gpa && (
                          <span className="text-xs bg-accent-100 text-accent-700 px-2 py-1 rounded">
                            GPA: {edu.gpa}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Certifications Section */}
            {certifications.length > 0 && (
              <section>
                <h2 className="text-xl font-bold text-primary-700 mb-4 pb-2 border-b-2 border-primary-200">
                  Certifications
                </h2>
                <div className="space-y-3">
                  {certifications.map((cert) => (
                    <div key={cert.id} className="bg-gray-50 p-3 rounded-lg">
                      <h3 className="font-semibold text-gray-900 text-sm">{cert.name}</h3>
                      <p className="text-gray-600 text-xs">{cert.issuer}</p>
                      <p className="text-xs text-gray-500">
                        <CalendarDays className="w-3 h-3 inline mr-1" />
                        {formatDate(cert.issueDate)}
                        {cert.expiryDate && ` - ${formatDate(cert.expiryDate)}`}
                      </p>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Languages Section */}
            {languages.length > 0 && (
              <section>
                <h2 className="text-xl font-bold text-primary-700 mb-4 pb-2 border-b-2 border-primary-200">
                  Languages
                </h2>
                <div className="space-y-2">
                  {languages.map((lang) => (
                    <div key={lang.id} className="flex justify-between items-center">
                      <span className="text-sm text-gray-700">{lang.name}</span>
                      <span className="text-xs bg-secondary-100 text-secondary-700 px-2 py-1 rounded capitalize">
                        {lang.proficiency}
                      </span>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>
        </div>
      </div>

      <style jsx>{`
        .clip-path-diagonal {
          clip-path: polygon(0 100%, 100% 0, 100% 100%, 0% 100%);
        }

        @media print {
          .clip-path-diagonal {
            clip-path: none;
          }
        }
      `}</style>
    </div>
  );
};

export default CreativeTemplate;