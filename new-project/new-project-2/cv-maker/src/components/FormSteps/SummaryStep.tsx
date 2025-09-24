import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useCV } from '@/contexts/CVContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/common/Card';
import { Label } from '@/components/common/Label';
import { Button } from '@/components/common/Button';
import { FileText, ArrowLeft, ArrowRight } from 'lucide-react';

const summarySchema = z.object({
  professionalSummary: z.string().min(10, 'Professional summary must be at least 10 characters'),
});

type SummaryFormData = z.infer<typeof summarySchema>;

export const SummaryStep: React.FC = () => {
  const { state, dispatch } = useCV();
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<SummaryFormData>({
    resolver: zodResolver(summarySchema),
    defaultValues: {
      professionalSummary: state.cvData.professionalSummary,
    },
  });

  const watchedSummary = watch('professionalSummary');

  const onSubmit = (data: SummaryFormData) => {
    dispatch({ type: 'UPDATE_PROFESSIONAL_SUMMARY', payload: data.professionalSummary });
    dispatch({ type: 'SET_CURRENT_STEP', payload: 'experience' });
  };

  const handlePrevious = () => {
    dispatch({ type: 'SET_CURRENT_STEP', payload: 'personal' });
  };

  
  const suggestions = [
    "Results-driven professional with X years of experience in [industry].",
    "Skilled in [key skills] with a proven track record of [achievement].",
    "Passionate about [industry/field] with expertise in [specific areas].",
    "Seeking to leverage my skills in [skill] to contribute to [company goal].",
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Professional Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="professionalSummary">
                Write a brief professional summary (2-3 sentences)
              </Label>
              <textarea
                id="professionalSummary"
                {...register('professionalSummary')}
                placeholder="Example: Experienced software developer with 5+ years of expertise in full-stack development. Passionate about creating scalable web applications and leading cross-functional teams..."
                className={`flex min-h-[120px] w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${
                  errors.professionalSummary ? 'border-red-500 focus-visible:ring-red-500' : ''
                }`}
                rows={4}
              />
              {errors.professionalSummary && (
                <p className="text-sm text-red-500">{errors.professionalSummary?.message}</p>
              )}
              <p className="text-sm text-gray-500">
                {watchedSummary?.length || 0} characters
              </p>
            </div>

            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Quick Suggestions:</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => {
                      // In a real app, this would append the suggestion to the textarea
                      // For now, it's just a placeholder
                    }}
                    className="text-left p-3 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors text-sm"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex justify-between pt-4">
              <Button type="button" variant="outline" onClick={handlePrevious}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Previous
              </Button>
              <Button type="submit">
                Next Step
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Live Preview */}
      <Card>
        <CardHeader>
          <CardTitle>Preview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-gray-50 p-4 rounded-md">
            <h3 className="font-semibold text-lg mb-2">
              {state.cvData.personalInfo.fullName || 'Your Name'}
            </h3>
            <p className="text-gray-700 text-sm leading-relaxed">
              {watchedSummary || 'Your professional summary will appear here...'}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};