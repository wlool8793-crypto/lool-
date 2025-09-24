import React from 'react';
import { CVData } from '@/types';
import { CalendarDays, MapPin, Mail, Phone, Globe, Github, Linkedin, Twitter, Award, Briefcase, GraduationCap } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ExecutiveTemplateProps {
  data: CVData;
  className?: string;
}

const ExecutiveTemplate: React.FC<ExecutiveTemplateProps> = ({ data, className }) => {
  const { personalInfo, professionalSummary, workExperience, education, skills, projects, certifications, languages, awards } = data;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short'
    });
  };

  const getSkillLevelColor = (level: string) => {
    switch (level) {
      case 'expert': return 'bg-primary-900';
      case 'advanced': return 'bg-primary-700';
      case 'intermediate': return 'bg-primary-500';
      case 'beginner': return 'bg-primary-300';
      default: return 'bg-primary-200';
    }
  };

  return (
    <div className={cn(
      'w-full max-w-4xl mx-auto bg-white shadow-lg print:shadow-none',
      'border border-gray-200',
      className
    )}>
      {/* Executive Header */}
      <div className="bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 text-white">
        <div className="p-8">
          <div className="flex flex-col md:flex-row items-center md:items-start gap-8">
            {personalInfo.profileImage && (
              <div className="flex-shrink-0">
                <img
                  src={personalInfo.profileImage}
                  alt={personalInfo.fullName}
                  className="w-32 h-32 rounded-lg border-2 border-gray-700 object-cover"
                />
              </div>
            )}
            <div className="flex-1 text-center md:text-left">
              <div className="mb-2">
                <span className="text-sm uppercase tracking-wider text-gray-400 mb-1 block">Executive Profile</span>
                <h1 className="text-3xl font-light tracking-wide mb-2">{personalInfo.fullName}</h1>
              </div>
              {personalInfo.headline && (
                <p className="text-xl text-gray-300 mb-4 font-light italic">{personalInfo.headline}</p>
              )}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                {personalInfo.email && (
                  <div className="flex items-center gap-2">
                    <Mail className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-300">{personalInfo.email}</span>
                  </div>
                )}
                {personalInfo.phone && (
                  <div className="flex items-center gap-2">
                    <Phone className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-300">{personalInfo.phone}</span>
                  </div>
                )}
                {personalInfo.address && (
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-300">{personalInfo.address}</span>
                  </div>
                )}
                {personalInfo.linkedin && (
                  <div className="flex items-center gap-2">
                    <Linkedin className="w-4 h-4 text-gray-400" />
                    <a href={personalInfo.linkedin} className="text-gray-300 hover:text-white transition-colors">
                      LinkedIn
                    </a>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="p-8">
        {/* Executive Summary */}
        {professionalSummary && (
          <section className="mb-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-0.5 bg-primary-700"></div>
              <h2 className="text-xl font-semibold text-gray-900 uppercase tracking-wider">Executive Summary</h2>
              <div className="flex-1 h-0.5 bg-gray-200"></div>
            </div>
            <div className="bg-gray-50 p-6 border-l-4 border-primary-700">
              <p className="text-gray-700 leading-relaxed text-justify">{professionalSummary}</p>
            </div>
          </section>
        )}

        {/* Core Competencies */}
        {skills.length > 0 && (
          <section className="mb-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-0.5 bg-primary-700"></div>
              <h2 className="text-xl font-semibold text-gray-900 uppercase tracking-wider">Core Competencies</h2>
              <div className="flex-1 h-0.5 bg-gray-200"></div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {skills.map((skill) => (
                <div key={skill.id} className="flex items-center gap-2">
                  <div className={cn('w-2 h-2 rounded-full', getSkillLevelColor(skill.level))}></div>
                  <span className="text-sm text-gray-700">{skill.name}</span>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Professional Experience */}
        {workExperience.length > 0 && (
          <section className="mb-8">
            <div className="flex items-center gap-3 mb-6">
              <Briefcase className="w-6 h-6 text-primary-700" />
              <h2 className="text-xl font-semibold text-gray-900 uppercase tracking-wider">Professional Experience</h2>
              <div className="flex-1 h-0.5 bg-gray-200"></div>
            </div>
            <div className="space-y-6">
              {workExperience.map((exp, index) => (
                <div key={exp.id} className="relative">
                  {index > 0 && <div className="absolute top-0 left-0 w-full h-px bg-gray-200"></div>}
                  <div className="pt-6">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{exp.position}</h3>
                        <p className="text-primary-700 font-medium">{exp.company}</p>
                        <p className="text-sm text-gray-600 flex items-center gap-1 mt-1">
                          <MapPin className="w-4 h-4" />
                          {exp.location}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-900">
                          {formatDate(exp.startDate)} - {exp.current ? 'Present' : formatDate(exp.endDate)}
                        </p>
                        <span className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded mt-1">
                          {exp.employmentType}
                        </span>
                      </div>
                    </div>
                    <p className="text-gray-700 mb-3 leading-relaxed">{exp.description}</p>
                    {exp.achievements.length > 0 && (
                      <div>
                        <h4 className="font-medium text-gray-800 mb-2">Key Achievements:</h4>
                        <ul className="list-disc list-inside text-gray-600 space-y-1">
                          {exp.achievements.map((achievement, index) => (
                            <li key={index} className="text-sm leading-relaxed">{achievement}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Two Column Layout for Education, Certifications, Awards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          {/* Education */}
          {education.length > 0 && (
            <section>
              <div className="flex items-center gap-3 mb-4">
                <GraduationCap className="w-5 h-5 text-primary-700" />
                <h2 className="text-lg font-semibold text-gray-900 uppercase tracking-wider">Education</h2>
              </div>
              <div className="space-y-4">
                {education.map((edu) => (
                  <div key={edu.id} className="border-l-2 border-gray-200 pl-4">
                    <h3 className="font-semibold text-gray-900">{edu.degree}</h3>
                    <p className="text-primary-600 text-sm">{edu.field}</p>
                    <p className="text-gray-600 text-sm">{edu.institution}</p>
                    <div className="flex justify-between items-center mt-2">
                      <p className="text-xs text-gray-500">
                        {formatDate(edu.startDate)} - {formatDate(edu.endDate)}
                      </p>
                      {edu.gpa && (
                        <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                          GPA: {edu.gpa}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Certifications */}
          {certifications.length > 0 && (
            <section>
              <div className="flex items-center gap-3 mb-4">
                <Award className="w-5 h-5 text-primary-700" />
                <h2 className="text-lg font-semibold text-gray-900 uppercase tracking-wider">Certifications</h2>
              </div>
              <div className="space-y-3">
                {certifications.map((cert) => (
                  <div key={cert.id} className="bg-gray-50 p-3 rounded border-l-2 border-primary-200">
                    <h3 className="font-medium text-gray-900 text-sm">{cert.name}</h3>
                    <p className="text-gray-600 text-xs">{cert.issuer}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {formatDate(cert.issueDate)}
                      {cert.expiryDate && ` - ${formatDate(cert.expiryDate)}`}
                    </p>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>

        {/* Awards & Recognition */}
        {awards.length > 0 && (
          <section className="mb-8">
            <div className="flex items-center gap-3 mb-4">
              <Award className="w-6 h-6 text-primary-700" />
              <h2 className="text-xl font-semibold text-gray-900 uppercase tracking-wider">Awards & Recognition</h2>
              <div className="flex-1 h-0.5 bg-gray-200"></div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {awards.map((award) => (
                <div key={award.id} className="bg-gradient-to-r from-gray-50 to-white p-4 rounded-lg border border-gray-200">
                  <h3 className="font-semibold text-gray-900">{award.name}</h3>
                  <p className="text-primary-600 text-sm">{award.issuer}</p>
                  <div className="flex justify-between items-center mt-2">
                    <p className="text-xs text-gray-500">{formatDate(award.date)}</p>
                    <span className="text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded">
                      {award.level}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Languages */}
        {languages.length > 0 && (
          <section>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-0.5 bg-primary-700"></div>
              <h2 className="text-xl font-semibold text-gray-900 uppercase tracking-wider">Languages</h2>
              <div className="flex-1 h-0.5 bg-gray-200"></div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {languages.map((lang) => (
                <div key={lang.id} className="text-center">
                  <p className="font-medium text-gray-900">{lang.name}</p>
                  <p className="text-sm text-gray-600 capitalize">{lang.proficiency}</p>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>

      {/* Footer */}
      <div className="bg-gray-50 border-t border-gray-200 p-4">
        <div className="text-center text-xs text-gray-500">
          This document contains confidential and proprietary information. All rights reserved.
        </div>
      </div>
    </div>
  );
};

export default ExecutiveTemplate;